"""Link snapshot service for capturing and storing link content."""

import asyncio
import gzip
import hashlib
import io
import magic
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union
from urllib.parse import urlparse

import httpx
from pydantic import ValidationError

from leenkz.models import HttpUrl, FtpUrl, S3Url, StorageUrl, CloudStorageUrl


@dataclass
class SnapshotData:
    """Snapshot data container."""
    content: bytes
    mime_type: str
    size_original: int
    size_compressed: int
    compression: str
    checksum: str
    encoding: Optional[str] = None
    last_modified: Optional[datetime] = None
    etag: Optional[str] = None


class SnapshotService:
    """Service for capturing link snapshots with compression."""
    
    def __init__(self, max_size_mb: int = 25, allowed_mime_regex: str = r".*"):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.allowed_mime_regex = re.compile(allowed_mime_regex)
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
            max_redirects=10
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def fetch_content(self, url: Union[HttpUrl, FtpUrl, S3Url, StorageUrl, CloudStorageUrl]) -> SnapshotData:
        """Fetch content from URL and return snapshot data."""
        if isinstance(url, HttpUrl):
            return await self._fetch_http(url)
        elif isinstance(url, FtpUrl):
            return await self._fetch_ftp(url)
        elif isinstance(url, S3Url):
            return await self._fetch_s3(url)
        else:
            # For storage URLs, treat as HTTP
            return await self._fetch_http(url)
    
    async def _fetch_http(self, url: Union[HttpUrl, StorageUrl, CloudStorageUrl]) -> SnapshotData:
        """Fetch content via HTTP/HTTPS."""
        try:
            response = await self.client.get(str(url))
            response.raise_for_status()
            
            content = response.content
            
            # Check size limit
            if len(content) > self.max_size_bytes:
                raise ValueError(f"Content too large: {len(content)} bytes (max: {self.max_size_bytes})")
            
            # Detect MIME type
            mime_type = self._detect_mime_type(content, response.headers.get("content-type"))
            
            # Validate MIME type
            if not self.allowed_mime_regex.match(mime_type):
                raise ValueError(f"MIME type not allowed: {mime_type}")
            
            # Get metadata
            last_modified = None
            if "last-modified" in response.headers:
                try:
                    last_modified = datetime.fromisoformat(
                        response.headers["last-modified"].replace("GMT", "+00:00")
                    )
                except ValueError:
                    pass
            
            return SnapshotData(
                content=content,
                mime_type=mime_type,
                size_original=len(content),
                size_compressed=len(content),  # Will be updated after compression
                compression="none",
                checksum=self._calculate_checksum(content),
                encoding=response.headers.get("content-encoding"),
                last_modified=last_modified,
                etag=response.headers.get("etag")
            )
            
        except httpx.HTTPStatusError as e:
            raise ValueError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise ValueError(f"Request error: {e}")
    
    async def _fetch_ftp(self, url: FtpUrl) -> SnapshotData:
        """Fetch content via FTP (placeholder - would need ftplib or similar)."""
        raise NotImplementedError("FTP fetching not yet implemented")
    
    async def _fetch_s3(self, url: S3Url) -> SnapshotData:
        """Fetch content from S3 (placeholder - would need boto3)."""
        raise NotImplementedError("S3 fetching not yet implemented")
    
    def _detect_mime_type(self, content: bytes, content_type_header: Optional[str] = None) -> str:
        """Detect MIME type from content and headers."""
        # Try content-type header first
        if content_type_header:
            # Extract MIME type from header (remove charset, etc.)
            mime_type = content_type_header.split(';')[0].strip()
            if mime_type and mime_type != 'application/octet-stream':
                return mime_type
        
        # Use python-magic for content-based detection
        try:
            mime_type = magic.from_buffer(content, mime=True)
            return mime_type
        except Exception:
            # Fallback to basic detection
            return self._basic_mime_detection(content)
    
    def _basic_mime_detection(self, content: bytes) -> str:
        """Basic MIME type detection based on content."""
        if not content:
            return "application/octet-stream"
        
        # Check for text content
        try:
            content.decode('utf-8')
            return "text/plain"
        except UnicodeDecodeError:
            pass
        
        # Check for common file signatures
        signatures = {
            b'\x89PNG\r\n\x1a\n': "image/png",
            b'\xff\xd8\xff': "image/jpeg",
            b'GIF87a': "image/gif",
            b'GIF89a': "image/gif",
            b'%PDF': "application/pdf",
            b'PK\x03\x04': "application/zip",
            b'\x1f\x8b\x08': "application/gzip",
            b'<!DOCTYPE': "text/html",
            b'<html': "text/html",
            b'<?xml': "application/xml",
        }
        
        for signature, mime_type in signatures.items():
            if content.startswith(signature):
                return mime_type
        
        return "application/octet-stream"
    
    def _calculate_checksum(self, content: bytes) -> str:
        """Calculate SHA-256 checksum of content."""
        return hashlib.sha256(content).hexdigest()
    
    def calculate_content_hash(self, content: bytes) -> str:
        """Calculate SHA-256 content hash for deduplication."""
        return hashlib.sha256(content).hexdigest().lower()
    
    def compress_content(self, snapshot_data: SnapshotData, compression: str = "gzip") -> SnapshotData:
        """Compress content using specified algorithm."""
        if compression == "none":
            return snapshot_data
        
        if compression == "gzip":
            compressed = gzip.compress(snapshot_data.content)
        elif compression == "zstd":
            try:
                import zstandard as zstd
                compressor = zstd.ZstdCompressor()
                compressed = compressor.compress(snapshot_data.content)
            except ImportError:
                raise ValueError("zstandard library not available")
        else:
            raise ValueError(f"Unsupported compression: {compression}")
        
        # Create new snapshot data with compressed content
        return SnapshotData(
            content=compressed,
            mime_type=snapshot_data.mime_type,
            size_original=snapshot_data.size_original,
            size_compressed=len(compressed),
            compression=compression,
            checksum=snapshot_data.checksum,
            encoding=snapshot_data.encoding,
            last_modified=snapshot_data.last_modified,
            etag=snapshot_data.etag
        )
    
    def decompress_content(self, snapshot_data: SnapshotData) -> bytes:
        """Decompress content."""
        if snapshot_data.compression == "none":
            return snapshot_data.content
        
        if snapshot_data.compression == "gzip":
            return gzip.decompress(snapshot_data.content)
        elif snapshot_data.compression == "zstd":
            try:
                import zstandard as zstd
                decompressor = zstd.ZstdDecompressor()
                return decompressor.decompress(snapshot_data.content)
            except ImportError:
                raise ValueError("zstandard library not available")
        else:
            raise ValueError(f"Unsupported compression: {snapshot_data.compression}")
    
    def is_text_content(self, mime_type: str) -> bool:
        """Check if content is text-based."""
        return mime_type.startswith(('text/', 'application/json', 'application/xml', 'application/javascript'))
    
    def is_image_content(self, mime_type: str) -> bool:
        """Check if content is an image."""
        return mime_type.startswith('image/')
    
    def can_preview_inline(self, mime_type: str) -> bool:
        """Check if content can be previewed inline."""
        return self.is_text_content(mime_type) or self.is_image_content(mime_type) 
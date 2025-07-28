"""Tests for snapshot functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from leenkz.core.snapshot import SnapshotService, SnapshotData
from leenkz.api.main import app


@pytest.fixture
def client():
    """Test client."""
    return TestClient(app)


@pytest.fixture
def mock_snapshot_service():
    """Mock snapshot service."""
    service = AsyncMock(spec=SnapshotService)
    
    # Mock snapshot data
    snapshot_data = SnapshotData(
        content=b"<html><body>Test content</body></html>",
        mime_type="text/html",
        size_original=35,
        size_compressed=35,
        compression="none",
        checksum="test-checksum",
        encoding=None,
        last_modified=None,
        etag=None,
    )
    
    service.fetch_content.return_value = snapshot_data
    service.compress_content.return_value = snapshot_data
    service.decompress_content.return_value = b"<html><body>Test content</body></html>"
    
    return service


class TestSnapshotService:
    """Test snapshot service functionality."""
    
    @pytest.mark.asyncio
    async def test_compress_gzip(self):
        """Test gzip compression."""
        service = SnapshotService()
        
        # Create test data
        original_data = SnapshotData(
            content=b"test content" * 1000,  # 12KB of data
            mime_type="text/plain",
            size_original=12000,
            size_compressed=12000,
            compression="none",
            checksum="test",
        )
        
        # Compress
        compressed_data = service.compress_content(original_data, "gzip")
        
        # Verify compression worked
        assert compressed_data.compression == "gzip"
        assert compressed_data.size_compressed < compressed_data.size_original
        assert len(compressed_data.content) < len(original_data.content)
        
        # Verify decompression works
        decompressed = service.decompress_content(compressed_data)
        assert decompressed == original_data.content
    
    @pytest.mark.asyncio
    async def test_compress_zstd(self):
        """Test zstd compression (if available)."""
        try:
            import zstandard
        except ImportError:
            pytest.skip("zstandard not available")
        
        service = SnapshotService()
        
        # Create test data
        original_data = SnapshotData(
            content=b"test content" * 1000,
            mime_type="text/plain",
            size_original=12000,
            size_compressed=12000,
            compression="none",
            checksum="test",
        )
        
        # Compress
        compressed_data = service.compress_content(original_data, "zstd")
        
        # Verify compression worked
        assert compressed_data.compression == "zstd"
        assert compressed_data.size_compressed < compressed_data.size_original
        
        # Verify decompression works
        decompressed = service.decompress_content(compressed_data)
        assert decompressed == original_data.content
    
    def test_mime_type_detection(self):
        """Test MIME type detection."""
        service = SnapshotService()
        
        # Test HTML detection
        html_content = b"<!DOCTYPE html><html><body>Test</body></html>"
        mime_type = service._detect_mime_type(html_content, "text/html; charset=utf-8")
        assert mime_type == "text/html"
        
        # Test JSON detection
        json_content = b'{"key": "value"}'
        mime_type = service._detect_mime_type(json_content, "application/json")
        assert mime_type == "application/json"
        
        # Test fallback detection
        text_content = b"plain text content"
        mime_type = service._detect_mime_type(text_content)
        assert mime_type == "text/plain"
    
    def test_content_type_checks(self):
        """Test content type checking methods."""
        service = SnapshotService()
        
        assert service.is_text_content("text/html")
        assert service.is_text_content("application/json")
        assert service.is_text_content("application/xml")
        assert not service.is_text_content("image/png")
        
        assert service.is_image_content("image/png")
        assert service.is_image_content("image/jpeg")
        assert not service.is_image_content("text/html")
        
        assert service.can_preview_inline("text/html")
        assert service.can_preview_inline("image/png")
        assert not service.can_preview_inline("application/pdf")


class TestSnapshotAPI:
    """Test snapshot API endpoints."""
    
    def test_create_snapshot_unauthorized(self, client):
        """Test creating snapshot without authentication."""
        response = client.post("/api/links/1/snapshot", json={"compression": "gzip"})
        assert response.status_code == 401
    
    def test_list_snapshots_unauthorized(self, client):
        """Test listing snapshots without authentication."""
        response = client.get("/api/links/1/snapshots")
        assert response.status_code == 401
    
    def test_get_snapshot_raw_unauthorized(self, client):
        """Test getting raw snapshot without authentication."""
        response = client.get("/api/snapshots/1/raw")
        assert response.status_code == 401
    
    def test_delete_snapshot_unauthorized(self, client):
        """Test deleting snapshot without authentication."""
        response = client.delete("/api/snapshots/1")
        assert response.status_code == 401
    
    def test_get_snapshot_render_unauthorized(self, client):
        """Test getting snapshot render without authentication."""
        response = client.get("/api/snapshots/1/render")
        assert response.status_code == 401
    
    def test_get_snapshot_unauthorized(self, client):
        """Test getting single snapshot without authentication."""
        response = client.get("/api/snapshots/1")
        assert response.status_code == 401


class TestSnapshotValidation:
    """Test snapshot validation."""
    
    def test_size_limit_validation(self):
        """Test size limit validation."""
        service = SnapshotService(max_size_mb=1)  # 1MB limit
        
        # Test with content under limit
        small_content = b"small content"
        assert len(small_content) < service.max_size_bytes
        
        # Test with content over limit
        large_content = b"x" * (service.max_size_bytes + 1)
        assert len(large_content) > service.max_size_bytes
    
    def test_mime_type_validation(self):
        """Test MIME type validation."""
        # Allow only text and images
        service = SnapshotService(allowed_mime_regex=r"^(text/|image/)")
        
        assert service.allowed_mime_regex.match("text/html")
        assert service.allowed_mime_regex.match("image/png")
        assert not service.allowed_mime_regex.match("application/pdf")
        assert not service.allowed_mime_regex.match("application/zip") 
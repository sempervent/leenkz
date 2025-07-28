"""S3-compatible URL models and validators."""

import re
from urllib.parse import urlparse


class S3Url(str):
    """S3-compatible URL validator supporting multiple vendors."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        """Custom Pydantic core schema for S3 URL validation."""
        from pydantic_core import core_schema
        
        return core_schema.with_info_after_validator_function(
            cls._validate_s3_url,
            handler(str),
            serialization=core_schema.str_schema(),
        )
    
    @classmethod
    def _validate_s3_url(cls, v: str, info) -> str:
        """Validate S3-compatible URL format."""
        if not isinstance(v, str):
            raise ValueError("S3 URL must be a string")
        
        # Parse the URL
        parsed = urlparse(v)
        
        # Check if it's a valid URL
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        
        # Supported S3-compatible schemes
        s3_schemes = {
            's3',           # AWS S3
            's3a',          # AWS S3 (alternative)
            's3n',          # AWS S3 (alternative)
            'https',        # HTTPS endpoints (common for S3-compatible services)
            'http',         # HTTP endpoints (for local/minio)
            'gs',           # Google Cloud Storage
            'az',           # Azure Blob Storage
            'swift',        # OpenStack Swift
            'minio',        # MinIO
            'wasb',         # Azure Blob Storage (alternative)
            'wasbs',        # Azure Blob Storage (secure)
            'cos',          # IBM Cloud Object Storage
            'oss',          # Alibaba Cloud OSS
            'b2',           # Backblaze B2
            'do',           # DigitalOcean Spaces
            'scw',          # Scaleway Object Storage
            'ceph',         # Ceph Object Gateway
            'seaweedfs',    # SeaweedFS
        }
        
        if parsed.scheme not in s3_schemes:
            raise ValueError(f"Unsupported S3-compatible scheme: {parsed.scheme}")
        
        # Validate bucket name format (basic check)
        if parsed.path:
            path_parts = parsed.path.strip('/').split('/', 1)
            bucket_name = path_parts[0]
            
            # Basic bucket name validation
            if not re.match(r'^[a-z0-9][a-z0-9.-]*[a-z0-9]$', bucket_name):
                raise ValueError(f"Invalid bucket name format: {bucket_name}")
            
            # Check for common S3-compatible patterns
            s3_patterns = [
                # AWS S3: s3://bucket/key
                r'^s3://[a-z0-9][a-z0-9.-]*[a-z0-9]/.*$',
                # HTTPS S3: https://bucket.s3.region.amazonaws.com/key
                r'^https://[a-z0-9][a-z0-9.-]*\.s3\.[a-z0-9-]+\.amazonaws\.com/.*$',
                # MinIO: http://minio-server:port/bucket/key
                r'^https?://[^/]+/[a-z0-9][a-z0-9.-]*[a-z0-9]/.*$',
                # Azure Blob: https://account.blob.core.windows.net/container/blob
                r'^https://[^/]+\.blob\.core\.windows\.net/[^/]+/.*$',
                # Google Cloud: gs://bucket/object
                r'^gs://[a-z0-9][a-z0-9.-]*[a-z0-9]/.*$',
                # DigitalOcean: https://bucket.region.digitaloceanspaces.com/key
                r'^https://[a-z0-9][a-z0-9.-]*\.[a-z0-9-]+\.digitaloceanspaces\.com/.*$',
                # Backblaze B2: https://bucket.s3.region.backblazeb2.com/key
                r'^https://[a-z0-9][a-z0-9.-]*\.s3\.[a-z0-9-]+\.backblazeb2\.com/.*$',
            ]
            
            # Check if URL matches any S3-compatible pattern
            url_matches_pattern = any(re.match(pattern, v) for pattern in s3_patterns)
            
            # For non-standard patterns, do basic validation
            if not url_matches_pattern:
                # Ensure there's at least a bucket and key
                if len(path_parts) < 2:
                    raise ValueError("S3 URL must include bucket and key")
        
        return v
    
    def __repr__(self) -> str:
        return f"S3Url({super().__repr__()})"
    
    @property
    def bucket(self) -> str:
        """Extract bucket name from S3 URL."""
        parsed = urlparse(self)
        path_parts = parsed.path.strip('/').split('/', 1)
        return path_parts[0] if path_parts else ""
    
    @property
    def key(self) -> str:
        """Extract object key from S3 URL."""
        parsed = urlparse(self)
        path_parts = parsed.path.strip('/').split('/', 1)
        return path_parts[1] if len(path_parts) > 1 else ""
    
    @property
    def scheme(self) -> str:
        """Extract scheme from S3 URL."""
        return urlparse(self).scheme
    
    @property
    def endpoint(self) -> str:
        """Extract endpoint from S3 URL."""
        parsed = urlparse(self)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def is_aws_s3(self) -> bool:
        """Check if URL is AWS S3."""
        return self.scheme in ('s3', 's3a', 's3n') or 'amazonaws.com' in self
    
    def is_azure_blob(self) -> bool:
        """Check if URL is Azure Blob Storage."""
        return self.scheme in ('az', 'wasb', 'wasbs') or 'blob.core.windows.net' in self
    
    def is_google_cloud(self) -> bool:
        """Check if URL is Google Cloud Storage."""
        return self.scheme == 'gs'
    
    def is_minio(self) -> bool:
        """Check if URL is MinIO (basic heuristic)."""
        return self.scheme in ('http', 'https') and not any(
            provider in self for provider in ['amazonaws.com', 'blob.core.windows.net', 'digitaloceanspaces.com']
        ) 
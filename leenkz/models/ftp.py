"""FTP URL models and validators."""

import re
from urllib.parse import urlparse


class FtpUrl(str):
    """FTP-compatible URL validator supporting various FTP protocols."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        """Custom Pydantic core schema for FTP URL validation."""
        from pydantic_core import core_schema
        
        return core_schema.with_info_after_validator_function(
            cls._validate_ftp_url,
            handler(str),
            serialization=core_schema.str_schema(),
        )
    
    @classmethod
    def _validate_ftp_url(cls, v: str, info) -> str:
        """Validate FTP-compatible URL format."""
        if not isinstance(v, str):
            raise ValueError("FTP URL must be a string")
        
        # Parse the URL
        parsed = urlparse(v)
        
        # Check if it's a valid URL
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        
        # Supported FTP-compatible schemes
        ftp_schemes = {
            'ftp',          # Standard FTP
            'ftps',         # FTP over SSL/TLS
            'sftp',         # SSH File Transfer Protocol
            'ftpes',        # FTP over explicit SSL/TLS
        }
        
        if parsed.scheme not in ftp_schemes:
            raise ValueError(f"Unsupported FTP-compatible scheme: {parsed.scheme}")
        
        # Validate hostname format
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("FTP URL must include a hostname")
        
        # Basic hostname validation
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', hostname):
            raise ValueError(f"Invalid hostname format: {hostname}")
        
        # Validate port if specified
        if parsed.port is not None:
            if not (1 <= parsed.port <= 65535):
                raise ValueError(f"Invalid port number: {parsed.port}")
        
        return v
    
    def __repr__(self) -> str:
        return f"FtpUrl({super().__repr__()})"
    
    @property
    def hostname(self) -> str:
        """Extract hostname from FTP URL."""
        return urlparse(self).hostname or ""
    
    @property
    def port(self) -> int:
        """Extract port from FTP URL."""
        parsed = urlparse(self)
        return parsed.port or self._get_default_port()
    
    @property
    def username(self) -> str:
        """Extract username from FTP URL."""
        return urlparse(self).username or ""
    
    @property
    def password(self) -> str:
        """Extract password from FTP URL."""
        return urlparse(self).password or ""
    
    @property
    def path(self) -> str:
        """Extract file path from FTP URL."""
        return urlparse(self).path or ""
    
    @property
    def scheme(self) -> str:
        """Extract scheme from FTP URL."""
        return urlparse(self).scheme
    
    def _get_default_port(self) -> int:
        """Get default port for the FTP scheme."""
        default_ports = {
            'ftp': 21,
            'ftps': 990,
            'sftp': 22,
            'ftpes': 21,
        }
        return default_ports.get(self.scheme, 21)
    
    def is_standard_ftp(self) -> bool:
        """Check if URL is standard FTP."""
        return self.scheme == 'ftp'
    
    def is_secure_ftp(self) -> bool:
        """Check if URL is secure FTP (FTPS)."""
        return self.scheme == 'ftps'
    
    def is_sftp(self) -> bool:
        """Check if URL is SFTP (SSH File Transfer Protocol)."""
        return self.scheme == 'sftp'
    
    def is_explicit_ftp(self) -> bool:
        """Check if URL is explicit FTP over SSL/TLS."""
        return self.scheme == 'ftpes'
    
    def has_credentials(self) -> bool:
        """Check if URL includes username/password."""
        return bool(self.username or self.password) 
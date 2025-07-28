"""HTTP URL models and validators."""

import re
from urllib.parse import urlparse


class HttpUrl(str):
    """HTTP-compatible URL validator supporting various HTTP protocols."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        """Custom Pydantic core schema for HTTP URL validation."""
        from pydantic_core import core_schema
        
        return core_schema.with_info_after_validator_function(
            cls._validate_http_url,
            handler(str),
            serialization=core_schema.str_schema(),
        )
    
    @classmethod
    def _validate_http_url(cls, v: str, info) -> str:
        """Validate HTTP-compatible URL format."""
        if not isinstance(v, str):
            raise ValueError("HTTP URL must be a string")
        
        # Parse the URL
        parsed = urlparse(v)
        
        # Check if it's a valid URL
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        
        # Supported HTTP-compatible schemes
        http_schemes = {
            'http',         # Standard HTTP
            'https',        # HTTP over SSL/TLS
            'http2',        # HTTP/2
            'https2',       # HTTP/2 over SSL/TLS
            'ws',           # WebSocket
            'wss',          # WebSocket Secure
        }
        
        if parsed.scheme not in http_schemes:
            raise ValueError(f"Unsupported HTTP-compatible scheme: {parsed.scheme}")
        
        # Validate hostname format
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("HTTP URL must include a hostname")
        
        # Basic hostname validation (allows IP addresses and domain names)
        if not re.match(r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*|(\d{1,3}\.){3}\d{1,3}|\[[0-9a-fA-F:]+\])$', hostname):
            raise ValueError(f"Invalid hostname format: {hostname}")
        
        # Validate port if specified
        if parsed.port is not None:
            if not (1 <= parsed.port <= 65535):
                raise ValueError(f"Invalid port number: {parsed.port}")
        
        return v
    
    def __repr__(self) -> str:
        return f"HttpUrl({super().__repr__()})"
    
    @property
    def hostname(self) -> str:
        """Extract hostname from HTTP URL."""
        return urlparse(self).hostname or ""
    
    @property
    def port(self) -> int:
        """Extract port from HTTP URL."""
        parsed = urlparse(self)
        return parsed.port or self._get_default_port()
    
    @property
    def path(self) -> str:
        """Extract path from HTTP URL."""
        return urlparse(self).path or "/"
    
    @property
    def query(self) -> str:
        """Extract query string from HTTP URL."""
        return urlparse(self).query or ""
    
    @property
    def fragment(self) -> str:
        """Extract fragment from HTTP URL."""
        return urlparse(self).fragment or ""
    
    @property
    def scheme(self) -> str:
        """Extract scheme from HTTP URL."""
        return urlparse(self).scheme
    
    def _get_default_port(self) -> int:
        """Get default port for the HTTP scheme."""
        default_ports = {
            'http': 80,
            'https': 443,
            'http2': 80,
            'https2': 443,
            'ws': 80,
            'wss': 443,
        }
        return default_ports.get(self.scheme, 80)
    
    def is_secure(self) -> bool:
        """Check if URL uses secure protocol (HTTPS/WSS)."""
        return self.scheme in ('https', 'https2', 'wss')
    
    def is_websocket(self) -> bool:
        """Check if URL is WebSocket protocol."""
        return self.scheme in ('ws', 'wss')
    
    def is_http2(self) -> bool:
        """Check if URL is HTTP/2 protocol."""
        return self.scheme in ('http2', 'https2')
    
    def has_query_params(self) -> bool:
        """Check if URL has query parameters."""
        return bool(self.query)
    
    def has_fragment(self) -> bool:
        """Check if URL has a fragment."""
        return bool(self.fragment)
    
    def is_ip_address(self) -> bool:
        """Check if hostname is an IP address."""
        return bool(re.match(r'^(\d{1,3}\.){3}\d{1,3}$', self.hostname))
    
    def is_ipv6_address(self) -> bool:
        """Check if hostname is an IPv6 address."""
        return bool(re.match(r'^\[[0-9a-fA-F:]+\]$', self.hostname)) 
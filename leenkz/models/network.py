"""Network protocol URL models and validators."""

import re
from urllib.parse import urlparse


class NtpUrl(str):
    """NTP (Network Time Protocol) URL validator."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        """Custom Pydantic core schema for NTP URL validation."""
        from pydantic_core import core_schema
        
        return core_schema.with_info_after_validator_function(
            cls._validate_ntp_url,
            handler(str),
            serialization=core_schema.str_schema(),
        )
    
    @classmethod
    def _validate_ntp_url(cls, v: str, info) -> str:
        """Validate NTP URL format."""
        if not isinstance(v, str):
            raise ValueError("NTP URL must be a string")
        
        # Parse the URL
        parsed = urlparse(v)
        
        # Check if it's a valid URL
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        
        # Supported NTP schemes
        ntp_schemes = {
            'ntp',          # NTP
            'ntps',         # NTP over SSL/TLS
        }
        
        if parsed.scheme not in ntp_schemes:
            raise ValueError(f"Unsupported NTP scheme: {parsed.scheme}")
        
        # Validate hostname format
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("NTP URL must include a hostname")
        
        # Basic hostname validation
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', hostname):
            raise ValueError(f"Invalid hostname format: {hostname}")
        
        # Validate port if specified
        if parsed.port is not None:
            if not (1 <= parsed.port <= 65535):
                raise ValueError(f"Invalid port number: {parsed.port}")
        
        return v
    
    def __repr__(self) -> str:
        return f"NtpUrl({super().__repr__()})"
    
    @property
    def hostname(self) -> str:
        """Extract hostname from NTP URL."""
        return urlparse(self).hostname or ""
    
    @property
    def port(self) -> int:
        """Extract port from NTP URL."""
        parsed = urlparse(self)
        return parsed.port or self._get_default_port()
    
    @property
    def scheme(self) -> str:
        """Extract scheme from NTP URL."""
        return urlparse(self).scheme
    
    def _get_default_port(self) -> int:
        """Get default port for the NTP scheme."""
        default_ports = {
            'ntp': 123,
            'ntps': 123,
        }
        return default_ports.get(self.scheme, 123)
    
    def is_secure(self) -> bool:
        """Check if URL uses secure protocol (NTPS)."""
        return self.scheme == 'ntps'


class DnsUrl(str):
    """DNS URL validator."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        """Custom Pydantic core schema for DNS URL validation."""
        from pydantic_core import core_schema
        
        return core_schema.with_info_after_validator_function(
            cls._validate_dns_url,
            handler(str),
            serialization=core_schema.str_schema(),
        )
    
    @classmethod
    def _validate_dns_url(cls, v: str, info) -> str:
        """Validate DNS URL format."""
        if not isinstance(v, str):
            raise ValueError("DNS URL must be a string")
        
        # Parse the URL
        parsed = urlparse(v)
        
        # Check if it's a valid URL
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        
        # Supported DNS schemes
        dns_schemes = {
            'dns',          # DNS
            'dns+https',    # DNS over HTTPS
            'dns+tls',      # DNS over TLS
        }
        
        if parsed.scheme not in dns_schemes:
            raise ValueError(f"Unsupported DNS scheme: {parsed.scheme}")
        
        # Validate hostname format
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("DNS URL must include a hostname")
        
        # Basic hostname validation
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', hostname):
            raise ValueError(f"Invalid hostname format: {hostname}")
        
        # Validate port if specified
        if parsed.port is not None:
            if not (1 <= parsed.port <= 65535):
                raise ValueError(f"Invalid port number: {parsed.port}")
        
        return v
    
    def __repr__(self) -> str:
        return f"DnsUrl({super().__repr__()})"
    
    @property
    def hostname(self) -> str:
        """Extract hostname from DNS URL."""
        return urlparse(self).hostname or ""
    
    @property
    def port(self) -> int:
        """Extract port from DNS URL."""
        parsed = urlparse(self)
        return parsed.port or self._get_default_port()
    
    @property
    def scheme(self) -> str:
        """Extract scheme from DNS URL."""
        return urlparse(self).scheme
    
    def _get_default_port(self) -> int:
        """Get default port for the DNS scheme."""
        default_ports = {
            'dns': 53,
            'dns+https': 443,
            'dns+tls': 853,
        }
        return default_ports.get(self.scheme, 53)
    
    def is_secure(self) -> bool:
        """Check if URL uses secure protocol (DoH/DoT)."""
        return self.scheme in ('dns+https', 'dns+tls')


class LdapUrl(str):
    """LDAP URL validator."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        """Custom Pydantic core schema for LDAP URL validation."""
        from pydantic_core import core_schema
        
        return core_schema.with_info_after_validator_function(
            cls._validate_ldap_url,
            handler(str),
            serialization=core_schema.str_schema(),
        )
    
    @classmethod
    def _validate_ldap_url(cls, v: str, info) -> str:
        """Validate LDAP URL format."""
        if not isinstance(v, str):
            raise ValueError("LDAP URL must be a string")
        
        # Parse the URL
        parsed = urlparse(v)
        
        # Check if it's a valid URL
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        
        # Supported LDAP schemes
        ldap_schemes = {
            'ldap',         # LDAP
            'ldaps',        # LDAP over SSL/TLS
        }
        
        if parsed.scheme not in ldap_schemes:
            raise ValueError(f"Unsupported LDAP scheme: {parsed.scheme}")
        
        # Validate hostname format
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("LDAP URL must include a hostname")
        
        # Basic hostname validation
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', hostname):
            raise ValueError(f"Invalid hostname format: {hostname}")
        
        # Validate port if specified
        if parsed.port is not None:
            if not (1 <= parsed.port <= 65535):
                raise ValueError(f"Invalid port number: {parsed.port}")
        
        return v
    
    def __repr__(self) -> str:
        return f"LdapUrl({super().__repr__()})"
    
    @property
    def hostname(self) -> str:
        """Extract hostname from LDAP URL."""
        return urlparse(self).hostname or ""
    
    @property
    def port(self) -> int:
        """Extract port from LDAP URL."""
        parsed = urlparse(self)
        return parsed.port or self._get_default_port()
    
    @property
    def username(self) -> str:
        """Extract username from LDAP URL."""
        return urlparse(self).username or ""
    
    @property
    def path(self) -> str:
        """Extract DN path from LDAP URL."""
        return urlparse(self).path or ""
    
    @property
    def scheme(self) -> str:
        """Extract scheme from LDAP URL."""
        return urlparse(self).scheme
    
    def _get_default_port(self) -> int:
        """Get default port for the LDAP scheme."""
        default_ports = {
            'ldap': 389,
            'ldaps': 636,
        }
        return default_ports.get(self.scheme, 389)
    
    def is_secure(self) -> bool:
        """Check if URL uses secure protocol (LDAPS)."""
        return self.scheme == 'ldaps'
    
    def has_credentials(self) -> bool:
        """Check if URL includes username/password."""
        return bool(self.username)
    
    def get_dn(self) -> str:
        """Extract Distinguished Name from path."""
        return self.path.strip('/')


class SmtpUrl(str):
    """SMTP URL validator."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        """Custom Pydantic core schema for SMTP URL validation."""
        from pydantic_core import core_schema
        
        return core_schema.with_info_after_validator_function(
            cls._validate_smtp_url,
            handler(str),
            serialization=core_schema.str_schema(),
        )
    
    @classmethod
    def _validate_smtp_url(cls, v: str, info) -> str:
        """Validate SMTP URL format."""
        if not isinstance(v, str):
            raise ValueError("SMTP URL must be a string")
        
        # Parse the URL
        parsed = urlparse(v)
        
        # Check if it's a valid URL
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        
        # Supported SMTP schemes
        smtp_schemes = {
            'smtp',         # SMTP
            'smtps',        # SMTP over SSL/TLS
            'submission',   # SMTP Submission
        }
        
        if parsed.scheme not in smtp_schemes:
            raise ValueError(f"Unsupported SMTP scheme: {parsed.scheme}")
        
        # Validate hostname format
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("SMTP URL must include a hostname")
        
        # Basic hostname validation
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', hostname):
            raise ValueError(f"Invalid hostname format: {hostname}")
        
        # Validate port if specified
        if parsed.port is not None:
            if not (1 <= parsed.port <= 65535):
                raise ValueError(f"Invalid port number: {parsed.port}")
        
        return v
    
    def __repr__(self) -> str:
        return f"SmtpUrl({super().__repr__()})"
    
    @property
    def hostname(self) -> str:
        """Extract hostname from SMTP URL."""
        return urlparse(self).hostname or ""
    
    @property
    def port(self) -> int:
        """Extract port from SMTP URL."""
        parsed = urlparse(self)
        return parsed.port or self._get_default_port()
    
    @property
    def username(self) -> str:
        """Extract username from SMTP URL."""
        return urlparse(self).username or ""
    
    @property
    def password(self) -> str:
        """Extract password from SMTP URL."""
        return urlparse(self).password or ""
    
    @property
    def scheme(self) -> str:
        """Extract scheme from SMTP URL."""
        return urlparse(self).scheme
    
    def _get_default_port(self) -> int:
        """Get default port for the SMTP scheme."""
        default_ports = {
            'smtp': 25,
            'smtps': 465,
            'submission': 587,
        }
        return default_ports.get(self.scheme, 25)
    
    def is_secure(self) -> bool:
        """Check if URL uses secure protocol (SMTPS/Submission)."""
        return self.scheme in ('smtps', 'submission')
    
    def has_credentials(self) -> bool:
        """Check if URL includes username/password."""
        return bool(self.username or self.password) 
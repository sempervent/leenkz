"""Git URL models and validators."""

import re
from urllib.parse import urlparse


class GitUrl(str):
    """Git-compatible URL validator supporting various Git protocols."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        """Custom Pydantic core schema for Git URL validation."""
        from pydantic_core import core_schema
        
        return core_schema.with_info_after_validator_function(
            cls._validate_git_url,
            handler(str),
            serialization=core_schema.str_schema(),
        )
    
    @classmethod
    def _validate_git_url(cls, v: str, info) -> str:
        """Validate Git-compatible URL format."""
        if not isinstance(v, str):
            raise ValueError("Git URL must be a string")
        
        # Parse the URL
        parsed = urlparse(v)
        
        # Check if it's a valid URL
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        
        # Supported Git-compatible schemes
        git_schemes = {
            'git',          # Git protocol
            'git+ssh',      # Git over SSH
            'git+http',     # Git over HTTP
            'git+https',    # Git over HTTPS
            'ssh',          # SSH (for Git)
            'http',         # HTTP (for Git)
            'https',        # HTTPS (for Git)
            'file',         # Local file system
        }
        
        if parsed.scheme not in git_schemes:
            raise ValueError(f"Unsupported Git-compatible scheme: {parsed.scheme}")
        
        # Validate hostname format (for non-file schemes)
        if parsed.scheme != 'file':
            hostname = parsed.hostname
            if not hostname:
                raise ValueError("Git URL must include a hostname")
            
            # Basic hostname validation
            if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', hostname):
                raise ValueError(f"Invalid hostname format: {hostname}")
        
        # Validate port if specified
        if parsed.port is not None:
            if not (1 <= parsed.port <= 65535):
                raise ValueError(f"Invalid port number: {parsed.port}")
        
        # Validate path for repository
        if not parsed.path or parsed.path == '/':
            raise ValueError("Git URL must include a repository path")
        
        return v
    
    def __repr__(self) -> str:
        return f"GitUrl({super().__repr__()})"
    
    @property
    def hostname(self) -> str:
        """Extract hostname from Git URL."""
        return urlparse(self).hostname or ""
    
    @property
    def port(self) -> int:
        """Extract port from Git URL."""
        parsed = urlparse(self)
        return parsed.port or self._get_default_port()
    
    @property
    def username(self) -> str:
        """Extract username from Git URL."""
        return urlparse(self).username or ""
    
    @property
    def path(self) -> str:
        """Extract repository path from Git URL."""
        return urlparse(self).path or ""
    
    @property
    def scheme(self) -> str:
        """Extract scheme from Git URL."""
        return urlparse(self).scheme
    
    def _get_default_port(self) -> int:
        """Get default port for the Git scheme."""
        default_ports = {
            'git': 9418,
            'git+ssh': 22,
            'git+http': 80,
            'git+https': 443,
            'ssh': 22,
            'http': 80,
            'https': 443,
            'file': None,
        }
        return default_ports.get(self.scheme, 22)
    
    def is_ssh(self) -> bool:
        """Check if URL uses SSH protocol."""
        return self.scheme in ('git+ssh', 'ssh')
    
    def is_http(self) -> bool:
        """Check if URL uses HTTP protocol."""
        return self.scheme in ('git+http', 'http')
    
    def is_https(self) -> bool:
        """Check if URL uses HTTPS protocol."""
        return self.scheme in ('git+https', 'https')
    
    def is_local(self) -> bool:
        """Check if URL is local file system."""
        return self.scheme == 'file'
    
    def is_secure(self) -> bool:
        """Check if URL uses secure protocol (HTTPS/SSH)."""
        return self.is_https() or self.is_ssh()
    
    def has_credentials(self) -> bool:
        """Check if URL includes username/password."""
        return bool(self.username)
    
    def get_repository_name(self) -> str:
        """Extract repository name from path."""
        path_parts = self.path.strip('/').split('/')
        if path_parts:
            repo_name = path_parts[-1]
            # Remove .git extension if present
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            return repo_name
        return ""
    
    def get_organization(self) -> str:
        """Extract organization/owner from path."""
        path_parts = self.path.strip('/').split('/')
        if len(path_parts) >= 2:
            return path_parts[-2]
        return ""
    
    def is_github(self) -> bool:
        """Check if URL is from GitHub."""
        return 'github.com' in self.hostname
    
    def is_gitlab(self) -> bool:
        """Check if URL is from GitLab."""
        return 'gitlab.com' in self.hostname or 'gitlab.' in self.hostname
    
    def is_bitbucket(self) -> bool:
        """Check if URL is from Bitbucket."""
        return 'bitbucket.org' in self.hostname or 'bitbucket.' in self.hostname
    
    def is_azure_devops(self) -> bool:
        """Check if URL is from Azure DevOps."""
        return 'dev.azure.com' in self.hostname or 'visualstudio.com' in self.hostname 
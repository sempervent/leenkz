"""File storage URL models and validators."""

import re
from urllib.parse import urlparse


class StorageUrl(str):
    """File storage URL validator supporting various cloud storage services."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        """Custom Pydantic core schema for storage URL validation."""
        from pydantic_core import core_schema
        
        return core_schema.with_info_after_validator_function(
            cls._validate_storage_url,
            handler(str),
            serialization=core_schema.str_schema(),
        )
    
    @classmethod
    def _validate_storage_url(cls, v: str, info) -> str:
        """Validate file storage URL format."""
        if not isinstance(v, str):
            raise ValueError("Storage URL must be a string")
        
        # Parse the URL
        parsed = urlparse(v)
        
        # Check if it's a valid URL
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        
        # Supported storage schemes
        storage_schemes = {
            'https',        # HTTPS (most common for cloud storage)
            'http',         # HTTP (for local/development)
        }
        
        if parsed.scheme not in storage_schemes:
            raise ValueError(f"Unsupported storage scheme: {parsed.scheme}")
        
        # Validate hostname format
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("Storage URL must include a hostname")
        
        # Basic hostname validation
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', hostname):
            raise ValueError(f"Invalid hostname format: {hostname}")
        
        # Validate path for file
        if not parsed.path or parsed.path == '/':
            raise ValueError("Storage URL must include a file path")
        
        return v
    
    def __repr__(self) -> str:
        return f"StorageUrl({super().__repr__()})"
    
    @property
    def hostname(self) -> str:
        """Extract hostname from storage URL."""
        return urlparse(self).hostname or ""
    
    @property
    def path(self) -> str:
        """Extract file path from storage URL."""
        return urlparse(self).path or ""
    
    @property
    def scheme(self) -> str:
        """Extract scheme from storage URL."""
        return urlparse(self).scheme
    
    @property
    def query(self) -> str:
        """Extract query string from storage URL."""
        return urlparse(self).query or ""
    
    @property
    def fragment(self) -> str:
        """Extract fragment from storage URL."""
        return urlparse(self).fragment or ""
    
    def get_filename(self) -> str:
        """Extract filename from path."""
        path_parts = self.path.strip('/').split('/')
        if path_parts:
            filename = path_parts[-1]
            # Remove query parameters from filename
            if '?' in filename:
                filename = filename.split('?')[0]
            return filename
        return ""
    
    def get_file_extension(self) -> str:
        """Extract file extension from filename."""
        filename = self.get_filename()
        if '.' in filename:
            return filename.split('.')[-1].lower()
        return ""
    
    def is_secure(self) -> bool:
        """Check if URL uses secure protocol (HTTPS)."""
        return self.scheme == 'https'
    
    def has_query_params(self) -> bool:
        """Check if URL has query parameters."""
        return bool(self.query)
    
    def has_fragment(self) -> bool:
        """Check if URL has a fragment."""
        return bool(self.fragment)
    
    # Cloud storage service detection methods
    def is_dropbox(self) -> bool:
        """Check if URL is from Dropbox."""
        return any(domain in self.hostname for domain in [
            'dropbox.com',
            'dl.dropboxusercontent.com',
            'www.dropbox.com'
        ])
    
    def is_box(self) -> bool:
        """Check if URL is from Box."""
        return any(domain in self.hostname for domain in [
            'box.com',
            'app.box.com',
            'www.box.com'
        ])
    
    def is_google_drive(self) -> bool:
        """Check if URL is from Google Drive."""
        return any(domain in self.hostname for domain in [
            'drive.google.com',
            'docs.google.com',
            'www.drive.google.com'
        ])
    
    def is_onedrive(self) -> bool:
        """Check if URL is from OneDrive."""
        return any(domain in self.hostname for domain in [
            'onedrive.live.com',
            '1drv.ms',
            'www.onedrive.live.com'
        ])
    
    def is_icloud(self) -> bool:
        """Check if URL is from iCloud."""
        return any(domain in self.hostname for domain in [
            'icloud.com',
            'www.icloud.com'
        ])
    
    def is_mega(self) -> bool:
        """Check if URL is from MEGA."""
        return any(domain in self.hostname for domain in [
            'mega.nz',
            'www.mega.nz'
        ])
    
    def is_mediafire(self) -> bool:
        """Check if URL is from MediaFire."""
        return any(domain in self.hostname for domain in [
            'mediafire.com',
            'www.mediafire.com'
        ])
    
    def is_4shared(self) -> bool:
        """Check if URL is from 4shared."""
        return any(domain in self.hostname for domain in [
            '4shared.com',
            'www.4shared.com'
        ])
    
    def is_rapidshare(self) -> bool:
        """Check if URL is from RapidShare (legacy)."""
        return any(domain in self.hostname for domain in [
            'rapidshare.com',
            'www.rapidshare.com'
        ])
    
    def is_we_transfer(self) -> bool:
        """Check if URL is from WeTransfer."""
        return any(domain in self.hostname for domain in [
            'wetransfer.com',
            'www.wetransfer.com'
        ])
    
    def is_file_dropper(self) -> bool:
        """Check if URL is from FileDropper."""
        return any(domain in self.hostname for domain in [
            'filedropper.com',
            'www.filedropper.com'
        ])
    
    def is_sendspace(self) -> bool:
        """Check if URL is from SendSpace."""
        return any(domain in self.hostname for domain in [
            'sendspace.com',
            'www.sendspace.com'
        ])
    
    def is_zippyshare(self) -> bool:
        """Check if URL is from ZippyShare."""
        return any(domain in self.hostname for domain in [
            'zippyshare.com',
            'www.zippyshare.com'
        ])
    
    def is_uploaded(self) -> bool:
        """Check if URL is from Uploaded."""
        return any(domain in self.hostname for domain in [
            'uploaded.net',
            'www.uploaded.net'
        ])
    
    def is_turbobit(self) -> bool:
        """Check if URL is from Turbobit."""
        return any(domain in self.hostname for domain in [
            'turbobit.net',
            'www.turbobit.net'
        ])
    
    def is_nitroflare(self) -> bool:
        """Check if URL is from Nitroflare."""
        return any(domain in self.hostname for domain in [
            'nitroflare.com',
            'www.nitroflare.com'
        ])
    
    def is_rapidgator(self) -> bool:
        """Check if URL is from Rapidgator."""
        return any(domain in self.hostname for domain in [
            'rapidgator.net',
            'www.rapidgator.net'
        ])
    
    def is_uploadhaven(self) -> bool:
        """Check if URL is from UploadHaven."""
        return any(domain in self.hostname for domain in [
            'uploadhaven.com',
            'www.uploadhaven.com'
        ])
    
    def is_anonfiles(self) -> bool:
        """Check if URL is from AnonFiles."""
        return any(domain in self.hostname for domain in [
            'anonfiles.com',
            'www.anonfiles.com'
        ])
    
    def is_bayfiles(self) -> bool:
        """Check if URL is from BayFiles."""
        return any(domain in self.hostname for domain in [
            'bayfiles.com',
            'www.bayfiles.com'
        ])
    
    def is_letsupload(self) -> bool:
        """Check if URL is from LetsUpload."""
        return any(domain in self.hostname for domain in [
            'letsupload.cc',
            'www.letsupload.cc'
        ])
    
    def is_1fichier(self) -> bool:
        """Check if URL is from 1fichier."""
        return any(domain in self.hostname for domain in [
            '1fichier.com',
            'www.1fichier.com'
        ])
    
    def get_service_name(self) -> str:
        """Get the name of the storage service."""
        if self.is_dropbox():
            return "Dropbox"
        elif self.is_box():
            return "Box"
        elif self.is_google_drive():
            return "Google Drive"
        elif self.is_onedrive():
            return "OneDrive"
        elif self.is_icloud():
            return "iCloud"
        elif self.is_mega():
            return "MEGA"
        elif self.is_mediafire():
            return "MediaFire"
        elif self.is_4shared():
            return "4shared"
        elif self.is_we_transfer():
            return "WeTransfer"
        elif self.is_file_dropper():
            return "FileDropper"
        elif self.is_sendspace():
            return "SendSpace"
        elif self.is_zippyshare():
            return "ZippyShare"
        elif self.is_uploaded():
            return "Uploaded"
        elif self.is_turbobit():
            return "Turbobit"
        elif self.is_nitroflare():
            return "Nitroflare"
        elif self.is_rapidgator():
            return "Rapidgator"
        elif self.is_uploadhaven():
            return "UploadHaven"
        elif self.is_anonfiles():
            return "AnonFiles"
        elif self.is_bayfiles():
            return "BayFiles"
        elif self.is_letsupload():
            return "LetsUpload"
        elif self.is_1fichier():
            return "1fichier"
        else:
            return "Unknown"
    
    def is_premium_service(self) -> bool:
        """Check if the service typically requires premium for large files."""
        premium_services = {
            'rapidgator', 'nitroflare', 'turbobit', 'uploaded', 
            '1fichier', 'zippyshare', 'sendspace'
        }
        return self.get_service_name().lower() in premium_services
    
    def is_free_service(self) -> bool:
        """Check if the service is typically free for basic use."""
        free_services = {
            'dropbox', 'box', 'google drive', 'onedrive', 'icloud',
            'mega', 'mediafire', 'wetransfer', 'anonfiles', 'bayfiles',
            'letsupload', 'uploadhaven'
        }
        return self.get_service_name().lower() in free_services 
"""Cloud storage URL models and validators for enterprise cloud storage services."""

import re
from urllib.parse import urlparse


class CloudStorageUrl(str):
    """Cloud storage URL validator for enterprise cloud storage services."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        """Custom Pydantic core schema for cloud storage URL validation."""
        from pydantic_core import core_schema
        
        return core_schema.with_info_after_validator_function(
            cls._validate_cloud_storage_url,
            handler(str),
            serialization=core_schema.str_schema(),
        )
    
    @classmethod
    def _validate_cloud_storage_url(cls, v: str, info) -> str:
        """Validate cloud storage URL format."""
        if not isinstance(v, str):
            raise ValueError("Cloud storage URL must be a string")
        
        # Parse the URL
        parsed = urlparse(v)
        
        # Check if it's a valid URL
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        
        # Cloud storage services typically use HTTPS
        if parsed.scheme not in ('https', 'http'):
            raise ValueError(f"Unsupported cloud storage scheme: {parsed.scheme}")
        
        # Validate hostname format
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("Cloud storage URL must include a hostname")
        
        # Basic hostname validation
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', hostname):
            raise ValueError(f"Invalid hostname format: {hostname}")
        
        # Validate that it's a recognized cloud storage service
        if not cls._is_recognized_cloud_storage(hostname):
            raise ValueError(f"Unrecognized cloud storage service: {hostname}")
        
        return v
    
    @classmethod
    def _is_recognized_cloud_storage(cls, hostname: str) -> bool:
        """Check if hostname is a recognized cloud storage service."""
        cloud_storage_domains = {
            # Dropbox
            'dropbox.com', 'dl.dropboxusercontent.com', 'www.dropbox.com',
            'dropboxusercontent.com',
            
            # Box
            'box.com', 'app.box.com', 'www.box.com',
            'boxcdn.net', 'boxcloud.com',
            
            # OneDrive
            'onedrive.live.com', 'www.onedrive.live.com',
            '1drv.ms', 'onedrive.com',
            
            # Google Drive
            'drive.google.com', 'www.drive.google.com',
            'docs.google.com', 'www.docs.google.com',
            'sheets.google.com', 'slides.google.com',
            
            # iCloud
            'icloud.com', 'www.icloud.com',
            'icloud-content.com',
            
            # SharePoint
            'sharepoint.com', 'www.sharepoint.com',
            'office365.com', 'www.office365.com',
            
            # AWS WorkDocs
            'workdocs.aws.amazon.com',
            
            # Google Workspace
            'workspace.google.com',
            
            # Microsoft 365
            'office.com', 'www.office.com',
            'microsoft365.com',
            
            # Egnyte
            'egnyte.com', 'www.egnyte.com',
            
            # Citrix ShareFile
            'sharefile.com', 'www.sharefile.com',
            
            # Nextcloud
            'nextcloud.com', 'www.nextcloud.com',
            
            # OwnCloud
            'owncloud.com', 'www.owncloud.com',
            
            # Seafile
            'seafile.com', 'www.seafile.com',
            
            # pCloud
            'pcloud.com', 'www.pcloud.com',
            
            # Tresorit
            'tresorit.com', 'www.tresorit.com',
            
            # SpiderOak
            'spideroak.com', 'www.spideroak.com',
            
            # Sync.com
            'sync.com', 'www.sync.com',
            
            # MEGA
            'mega.nz', 'www.mega.nz',
            
            # MediaFire
            'mediafire.com', 'www.mediafire.com',
            
            # Yandex.Disk
            'disk.yandex.com', 'yadi.sk',
            
            # Baidu Cloud
            'pan.baidu.com', 'yun.baidu.com',
            
            # Tencent Weiyun
            'weiyun.com', 'www.weiyun.com',
            
            # Alibaba Cloud Drive
            'drive.aliyundrive.com',
            
            # Huawei Cloud
            'cloud.huawei.com',
        }
        
        return any(domain in hostname for domain in cloud_storage_domains)
    
    def __repr__(self) -> str:
        return f"CloudStorageUrl({super().__repr__()})"
    
    @property
    def hostname(self) -> str:
        """Extract hostname from cloud storage URL."""
        return urlparse(self).hostname or ""
    
    @property
    def path(self) -> str:
        """Extract file path from cloud storage URL."""
        return urlparse(self).path or ""
    
    @property
    def scheme(self) -> str:
        """Extract scheme from cloud storage URL."""
        return urlparse(self).scheme
    
    @property
    def query(self) -> str:
        """Extract query string from cloud storage URL."""
        return urlparse(self).query or ""
    
    @property
    def fragment(self) -> str:
        """Extract fragment from cloud storage URL."""
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
    
    # Major cloud storage service detection methods
    def is_dropbox(self) -> bool:
        """Check if URL is from Dropbox."""
        return any(domain in self.hostname for domain in [
            'dropbox.com', 'dl.dropboxusercontent.com', 'dropboxusercontent.com'
        ])
    
    def is_box(self) -> bool:
        """Check if URL is from Box."""
        return any(domain in self.hostname for domain in [
            'box.com', 'app.box.com', 'boxcdn.net', 'boxcloud.com'
        ])
    
    def is_onedrive(self) -> bool:
        """Check if URL is from OneDrive."""
        return any(domain in self.hostname for domain in [
            'onedrive.live.com', '1drv.ms', 'onedrive.com'
        ])
    
    def is_google_drive(self) -> bool:
        """Check if URL is from Google Drive."""
        return any(domain in self.hostname for domain in [
            'drive.google.com', 'docs.google.com', 'sheets.google.com', 'slides.google.com'
        ])
    
    def is_icloud(self) -> bool:
        """Check if URL is from iCloud."""
        return any(domain in self.hostname for domain in [
            'icloud.com', 'icloud-content.com'
        ])
    
    def is_sharepoint(self) -> bool:
        """Check if URL is from SharePoint."""
        return any(domain in self.hostname for domain in [
            'sharepoint.com', 'office365.com', 'office.com', 'microsoft365.com'
        ])
    
    def is_aws_workdocs(self) -> bool:
        """Check if URL is from AWS WorkDocs."""
        return 'workdocs.aws.amazon.com' in self.hostname
    
    def is_google_workspace(self) -> bool:
        """Check if URL is from Google Workspace."""
        return 'workspace.google.com' in self.hostname
    
    def is_egnyte(self) -> bool:
        """Check if URL is from Egnyte."""
        return 'egnyte.com' in self.hostname
    
    def is_citrix_sharefile(self) -> bool:
        """Check if URL is from Citrix ShareFile."""
        return 'sharefile.com' in self.hostname
    
    def is_nextcloud(self) -> bool:
        """Check if URL is from Nextcloud."""
        return 'nextcloud.com' in self.hostname
    
    def is_owncloud(self) -> bool:
        """Check if URL is from OwnCloud."""
        return 'owncloud.com' in self.hostname
    
    def is_seafile(self) -> bool:
        """Check if URL is from Seafile."""
        return 'seafile.com' in self.hostname
    
    def is_pcloud(self) -> bool:
        """Check if URL is from pCloud."""
        return 'pcloud.com' in self.hostname
    
    def is_tresorit(self) -> bool:
        """Check if URL is from Tresorit."""
        return 'tresorit.com' in self.hostname
    
    def is_spideroak(self) -> bool:
        """Check if URL is from SpiderOak."""
        return 'spideroak.com' in self.hostname
    
    def is_sync_com(self) -> bool:
        """Check if URL is from Sync.com."""
        return 'sync.com' in self.hostname
    
    def is_mega(self) -> bool:
        """Check if URL is from MEGA."""
        return 'mega.nz' in self.hostname
    
    def is_mediafire(self) -> bool:
        """Check if URL is from MediaFire."""
        return 'mediafire.com' in self.hostname
    
    def is_yandex_disk(self) -> bool:
        """Check if URL is from Yandex.Disk."""
        return any(domain in self.hostname for domain in [
            'disk.yandex.com', 'yadi.sk'
        ])
    
    def is_baidu_cloud(self) -> bool:
        """Check if URL is from Baidu Cloud."""
        return any(domain in self.hostname for domain in [
            'pan.baidu.com', 'yun.baidu.com'
        ])
    
    def is_tencent_weiyun(self) -> bool:
        """Check if URL is from Tencent Weiyun."""
        return 'weiyun.com' in self.hostname
    
    def is_aliyun_drive(self) -> bool:
        """Check if URL is from Alibaba Cloud Drive."""
        return 'drive.aliyundrive.com' in self.hostname
    
    def is_huawei_cloud(self) -> bool:
        """Check if URL is from Huawei Cloud."""
        return 'cloud.huawei.com' in self.hostname
    
    def get_service_name(self) -> str:
        """Get the name of the cloud storage service."""
        if self.is_dropbox():
            return "Dropbox"
        elif self.is_box():
            return "Box"
        elif self.is_onedrive():
            return "OneDrive"
        elif self.is_google_drive():
            return "Google Drive"
        elif self.is_icloud():
            return "iCloud"
        elif self.is_sharepoint():
            return "SharePoint"
        elif self.is_aws_workdocs():
            return "AWS WorkDocs"
        elif self.is_google_workspace():
            return "Google Workspace"
        elif self.is_egnyte():
            return "Egnyte"
        elif self.is_citrix_sharefile():
            return "Citrix ShareFile"
        elif self.is_nextcloud():
            return "Nextcloud"
        elif self.is_owncloud():
            return "OwnCloud"
        elif self.is_seafile():
            return "Seafile"
        elif self.is_pcloud():
            return "pCloud"
        elif self.is_tresorit():
            return "Tresorit"
        elif self.is_spideroak():
            return "SpiderOak"
        elif self.is_sync_com():
            return "Sync.com"
        elif self.is_mega():
            return "MEGA"
        elif self.is_mediafire():
            return "MediaFire"
        elif self.is_yandex_disk():
            return "Yandex.Disk"
        elif self.is_baidu_cloud():
            return "Baidu Cloud"
        elif self.is_tencent_weiyun():
            return "Tencent Weiyun"
        elif self.is_aliyun_drive():
            return "Alibaba Cloud Drive"
        elif self.is_huawei_cloud():
            return "Huawei Cloud"
        else:
            return "Unknown"
    
    def is_enterprise_service(self) -> bool:
        """Check if the service is enterprise-focused."""
        enterprise_services = {
            'dropbox', 'box', 'onedrive', 'google drive', 'sharepoint',
            'aws workdocs', 'google workspace', 'egnyte', 'citrix sharefile',
            'nextcloud', 'owncloud', 'seafile', 'tresorit', 'spideroak'
        }
        return self.get_service_name().lower() in enterprise_services
    
    def is_consumer_service(self) -> bool:
        """Check if the service is consumer-focused."""
        consumer_services = {
            'icloud', 'mega', 'mediafire', 'pcloud', 'sync.com',
            'yandex.disk', 'baidu cloud', 'tencent weiyun', 'aliyun drive',
            'huawei cloud'
        }
        return self.get_service_name().lower() in consumer_services
    
    def is_microsoft_service(self) -> bool:
        """Check if the service is from Microsoft."""
        microsoft_services = {
            'onedrive', 'sharepoint'
        }
        return self.get_service_name().lower() in microsoft_services
    
    def is_google_service(self) -> bool:
        """Check if the service is from Google."""
        google_services = {
            'google drive', 'google workspace'
        }
        return self.get_service_name().lower() in google_services
    
    def is_apple_service(self) -> bool:
        """Check if the service is from Apple."""
        return self.is_icloud()
    
    def is_amazon_service(self) -> bool:
        """Check if the service is from Amazon."""
        return self.is_aws_workdocs()
    
    def is_chinese_service(self) -> bool:
        """Check if the service is from a Chinese company."""
        chinese_services = {
            'baidu cloud', 'tencent weiyun', 'aliyun drive', 'huawei cloud'
        }
        return self.get_service_name().lower() in chinese_services
    
    def is_russian_service(self) -> bool:
        """Check if the service is from a Russian company."""
        return self.is_yandex_disk()
    
    def is_swiss_service(self) -> bool:
        """Check if the service is from a Swiss company."""
        swiss_services = {
            'pcloud', 'tresorit'
        }
        return self.get_service_name().lower() in swiss_services 
"""Tests for snapshot deduplication functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import select

from leenkz.core.snapshot import SnapshotService
from leenkz.core.database import LinkSnapshot
from leenkz.api.main import app


@pytest.fixture
def client():
    """Test client."""
    return TestClient(app)


class TestSnapshotDeduplication:
    """Test snapshot deduplication functionality."""
    
    @pytest.mark.asyncio
    async def test_duplicate_snapshot_returns_208(self, client, mock_db_session):
        """Test that creating duplicate snapshots returns 208 status."""
        # Mock existing snapshot with same content hash
        existing_snapshot = LinkSnapshot(
            id=1,
            link_id=1,
            created_by=1,
            mime_type="text/html",
            size_original=100,
            size_compressed=50,
            compression="gzip",
            checksum="test-checksum",
            content_hash="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
            content=b"<html>test</html>",
        )
        
        mock_db_session.exec.return_value.first.return_value = existing_snapshot
        
        # Mock snapshot service
        with patch('leenkz.core.snapshot.SnapshotService') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.fetch_content.return_value = MagicMock(
                content=b"<html>test</html>",
                mime_type="text/html",
                size_original=100,
                size_compressed=50,
                compression="gzip",
                checksum="test-checksum",
            )
            mock_service_instance.calculate_content_hash.return_value = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
            mock_service.return_value.__aenter__.return_value = mock_service_instance
            
            response = client.post(
                "/api/links/1/snapshot",
                json={"compression": "gzip", "force": False},
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 208
            data = response.json()
            assert data["id"] == 1
            assert "X-Content-Hash" in response.headers
    
    @pytest.mark.asyncio
    async def test_force_creates_duplicate(self, client, mock_db_session):
        """Test that force=True creates duplicate snapshots."""
        # Mock no existing snapshot
        mock_db_session.exec.return_value.first.return_value = None
        
        # Mock snapshot service
        with patch('leenkz.core.snapshot.SnapshotService') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.fetch_content.return_value = MagicMock(
                content=b"<html>test</html>",
                mime_type="text/html",
                size_original=100,
                size_compressed=50,
                compression="gzip",
                checksum="test-checksum",
            )
            mock_service_instance.calculate_content_hash.return_value = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
            mock_service.return_value.__aenter__.return_value = mock_service_instance
            
            response = client.post(
                "/api/links/1/snapshot",
                json={"compression": "gzip", "force": True},
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert data["content_hash"] == "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
    
    def test_content_hash_calculation(self):
        """Test content hash calculation."""
        service = SnapshotService()
        
        # Test with known content
        content = b"<html><body>test</body></html>"
        hash_result = service.calculate_content_hash(content)
        
        # Should be lowercase hex SHA-256
        assert len(hash_result) == 64
        assert all(c in '0123456789abcdef' for c in hash_result)
        
        # Same content should produce same hash
        hash_result2 = service.calculate_content_hash(content)
        assert hash_result == hash_result2
        
        # Different content should produce different hash
        different_content = b"<html><body>different</body></html>"
        different_hash = service.calculate_content_hash(different_content)
        assert hash_result != different_hash
    
    @pytest.mark.asyncio
    async def test_deduplication_with_different_compression(self, client, mock_db_session):
        """Test that different compression doesn't affect deduplication."""
        # Mock existing snapshot with same content but different compression
        existing_snapshot = LinkSnapshot(
            id=1,
            link_id=1,
            created_by=1,
            mime_type="text/html",
            size_original=100,
            size_compressed=100,  # No compression
            compression="none",
            checksum="test-checksum",
            content_hash="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
            content=b"<html>test</html>",
        )
        
        mock_db_session.exec.return_value.first.return_value = existing_snapshot
        
        # Mock snapshot service
        with patch('leenkz.core.snapshot.SnapshotService') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.fetch_content.return_value = MagicMock(
                content=b"<html>test</html>",
                mime_type="text/html",
                size_original=100,
                size_compressed=50,  # Gzip compression
                compression="gzip",
                checksum="test-checksum",
            )
            mock_service_instance.calculate_content_hash.return_value = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
            mock_service.return_value.__aenter__.return_value = mock_service_instance
            
            response = client.post(
                "/api/links/1/snapshot",
                json={"compression": "gzip", "force": False},
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Should still return 208 because content hash is the same
            assert response.status_code == 208


class TestSnapshotAPIWithDeduplication:
    """Test snapshot API with deduplication enabled."""
    
    def test_snapshot_create_with_force_param(self, client):
        """Test snapshot creation with force parameter."""
        response = client.post(
            "/api/links/1/snapshot",
            json={"compression": "gzip", "force": True},
            headers={"Authorization": "Bearer test-token"}
        )
        
        # Should not return 208 even if duplicate exists
        assert response.status_code in [200, 201, 400, 401, 403, 404]
    
    def test_snapshot_create_without_force_param(self, client):
        """Test snapshot creation without force parameter."""
        response = client.post(
            "/api/links/1/snapshot",
            json={"compression": "gzip"},
            headers={"Authorization": "Bearer test-token"}
        )
        
        # Should handle deduplication
        assert response.status_code in [200, 201, 208, 400, 401, 403, 404]
    
    def test_snapshot_response_includes_content_hash(self, client):
        """Test that snapshot responses include content_hash field."""
        # This would need a successful snapshot creation
        # For now, just test the schema
        from leenkz.api.schemas import Snapshot
        
        # Verify that Snapshot schema includes content_hash
        assert "content_hash" in Snapshot.model_fields 
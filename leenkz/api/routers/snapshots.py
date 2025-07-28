"""Snapshot API router."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlmodel import Session

from leenkz.api.deps import get_current_user, get_db
from leenkz.api.schemas import Snapshot, SnapshotCreate
from leenkz.core.database import Link, LinkSnapshot, User
from leenkz.core.snapshot import SnapshotService

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


@router.post("/links/{link_id}/snapshot", response_model=Snapshot)
async def create_snapshot(
    link_id: int,
    snapshot_data: SnapshotCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a snapshot for a link."""
    # Get the link
    link = await db.get(Link, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Check if user owns the link or is admin
    if link.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to snapshot this link")
    
    # Initialize snapshot service
    async with SnapshotService() as snapshot_service:
        try:
            # Fetch content from the link
            snapshot_data_fetched = await snapshot_service.fetch_content(link.url)
            
            # Calculate content hash for deduplication
            content_hash = snapshot_service.calculate_content_hash(snapshot_data_fetched.content)
            
            # Check for existing snapshot with same content (unless force=True)
            if not snapshot_data.force:
                existing_snapshot = await db.exec(
                    select(LinkSnapshot)
                    .where(LinkSnapshot.link_id == link_id)
                    .where(LinkSnapshot.content_hash == content_hash)
                    .order_by(LinkSnapshot.created_at.desc())
                    .limit(1)
                ).first()
                
                if existing_snapshot:
                    # Return existing snapshot with 208 status
                    return Response(
                        content=Snapshot.model_validate(existing_snapshot).model_dump_json(),
                        status_code=208,
                        media_type="application/json",
                        headers={"X-Content-Hash": content_hash}
                    )
            
            # Apply compression if requested
            if snapshot_data.compression != "none":
                snapshot_data_fetched = snapshot_service.compress_content(
                    snapshot_data_fetched, snapshot_data.compression
                )
            
            # Create snapshot record
            snapshot = LinkSnapshot(
                link_id=link_id,
                created_by=current_user.id,
                mime_type=snapshot_data_fetched.mime_type,
                size_original=snapshot_data_fetched.size_original,
                size_compressed=snapshot_data_fetched.size_compressed,
                compression=snapshot_data_fetched.compression,
                checksum=snapshot_data_fetched.checksum,
                content_hash=content_hash,
                encoding=snapshot_data_fetched.encoding,
                last_modified=snapshot_data_fetched.last_modified,
                etag=snapshot_data_fetched.etag,
                content=snapshot_data_fetched.content,
            )
            
            db.add(snapshot)
            await db.commit()
            await db.refresh(snapshot)
            
            return Snapshot.model_validate(snapshot)
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create snapshot: {str(e)}")


@router.get("/links/{link_id}/snapshots", response_model=List[Snapshot])
async def list_snapshots(
    link_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all snapshots for a link."""
    # Get the link
    link = await db.get(Link, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Check if user owns the link or is admin
    if link.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to view snapshots for this link")
    
    # Get snapshots
    statement = select(LinkSnapshot).where(LinkSnapshot.link_id == link_id).order_by(LinkSnapshot.created_at.desc())
    result = await db.exec(statement)
    snapshots = result.all()
    
    return [Snapshot.model_validate(snapshot) for snapshot in snapshots]


@router.get("/{snapshot_id}", response_model=Snapshot)
async def get_snapshot(
    snapshot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single snapshot by ID."""
    # Get the snapshot
    snapshot = await db.get(LinkSnapshot, snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    # Get the link to check permissions
    link = await db.get(Link, snapshot.link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Check if user owns the link or is admin
    if link.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to view this snapshot")
    
    return Snapshot.model_validate(snapshot)


@router.get("/{snapshot_id}/raw")
async def get_snapshot_raw(
    snapshot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get raw snapshot content."""
    # Get the snapshot
    snapshot = await db.get(LinkSnapshot, snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    # Get the link to check permissions
    link = await db.get(Link, snapshot.link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Check if user owns the link or is admin
    if link.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to view this snapshot")
    
    # Initialize snapshot service for decompression
    async with SnapshotService() as snapshot_service:
        try:
            # Create snapshot data object
            from leenkz.core.snapshot import SnapshotData
            snapshot_data = SnapshotData(
                content=snapshot.content,
                mime_type=snapshot.mime_type,
                size_original=snapshot.size_original,
                size_compressed=snapshot.size_compressed,
                compression=snapshot.compression,
                checksum=snapshot.checksum,
                encoding=snapshot.encoding,
                last_modified=snapshot.last_modified,
                etag=snapshot.etag,
            )
            
            # Decompress content
            raw_content = snapshot_service.decompress_content(snapshot_data)
            
            # Set response headers - serve decompressed bytes
            headers = {
                "Content-Type": snapshot.mime_type,
                "Content-Length": str(len(raw_content)),
                "X-Snapshot-Id": str(snapshot.id),
                "X-Original-Size": str(snapshot.size_original),
                "X-Leenkz-Compression": snapshot.compression,
                "X-Checksum": snapshot.checksum,
            }
            
            if snapshot.etag:
                headers["ETag"] = snapshot.etag
            
            if snapshot.last_modified:
                headers["Last-Modified"] = snapshot.last_modified.isoformat()
            
            return Response(
                content=raw_content,
                headers=headers,
                media_type=snapshot.mime_type,
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve snapshot: {str(e)}")


@router.get("/{snapshot_id}/render")
async def get_snapshot_render(
    snapshot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get snapshot content for in-browser rendering."""
    # Get the snapshot
    snapshot = await db.get(LinkSnapshot, snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    # Get the link to check permissions
    link = await db.get(Link, snapshot.link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Check if user owns the link or is admin
    if link.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to view this snapshot")
    
    # Check if content is renderable
    renderable_types = [
        "text/html", "text/markdown", "text/plain", 
        "text/css", "text/javascript", "application/json",
        "application/xml", "text/xml"
    ]
    
    is_renderable = (
        snapshot.mime_type in renderable_types or 
        snapshot.mime_type.startswith("image/")
    )
    
    if not is_renderable:
        raise HTTPException(
            status_code=415, 
            detail=f"Content type '{snapshot.mime_type}' is not renderable in browser"
        )
    
    # Initialize snapshot service for decompression
    async with SnapshotService() as snapshot_service:
        try:
            # Create snapshot data object
            from leenkz.core.snapshot import SnapshotData
            snapshot_data = SnapshotData(
                content=snapshot.content,
                mime_type=snapshot.mime_type,
                size_original=snapshot.size_original,
                size_compressed=snapshot.size_compressed,
                compression=snapshot.compression,
                checksum=snapshot.checksum,
                encoding=snapshot.encoding,
                last_modified=snapshot.last_modified,
                etag=snapshot.etag,
            )
            
            # Decompress content
            raw_content = snapshot_service.decompress_content(snapshot_data)
            
            # Set response headers for rendering
            headers = {
                "Content-Type": snapshot.mime_type,
                "Content-Length": str(len(raw_content)),
                "X-Snapshot-Id": str(snapshot.id),
                "X-Original-Size": str(snapshot.size_original),
                "X-Leenkz-Compression": snapshot.compression,
                "X-Checksum": snapshot.checksum,
                "X-Leenkz-Renderable": "true",
            }
            
            if snapshot.etag:
                headers["ETag"] = snapshot.etag
            
            if snapshot.last_modified:
                headers["Last-Modified"] = snapshot.last_modified.isoformat()
            
            return Response(
                content=raw_content,
                headers=headers,
                media_type=snapshot.mime_type,
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve snapshot: {str(e)}")


@router.delete("/{snapshot_id}")
async def delete_snapshot(
    snapshot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a snapshot."""
    # Get the snapshot
    snapshot = await db.get(LinkSnapshot, snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    # Get the link to check permissions
    link = await db.get(Link, snapshot.link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Check if user owns the link or is admin
    if link.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to delete this snapshot")
    
    # Delete the snapshot
    await db.delete(snapshot)
    await db.commit()
    
    return {"message": "Snapshot deleted successfully"} 
import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { Download, Eye, Trash2, FileText, Image, File } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { toast } from 'sonner';

interface Snapshot {
  id: number;
  mime_type: string;
  size_original: number;
  size_compressed: number;
  compression: string;
  content_hash: string;
  created_at: string;
}

interface SnapshotListProps {
  linkId: number;
  onSnapshotDeleted?: () => void;
}

export function SnapshotList({ linkId, onSnapshotDeleted }: SnapshotListProps) {
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchSnapshots();
  }, [linkId]);

  const fetchSnapshots = async () => {
    try {
      const response = await fetch(`/api/links/${linkId}/snapshots`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch snapshots');
      }

      const data = await response.json();
      setSnapshots(data);
    } catch (error) {
      toast.error('Failed to load snapshots');
    } finally {
      setIsLoading(false);
    }
  };

  const deleteSnapshot = async (snapshotId: number) => {
    try {
      const response = await fetch(`/api/snapshots/${snapshotId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete snapshot');
      }

      toast.success('Snapshot deleted successfully');
      onSnapshotDeleted?.();
      fetchSnapshots();
    } catch (error) {
      toast.error('Failed to delete snapshot');
    }
  };

  const downloadSnapshot = async (snapshotId: number, filename: string) => {
    try {
      const response = await fetch(`/api/snapshots/${snapshotId}/raw`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to download snapshot');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      toast.error('Failed to download snapshot');
    }
  };

  const viewSnapshot = (snapshotId: number) => {
    // Navigate to the snapshot viewer page
    window.location.href = `/snapshots/${snapshotId}`;
  };

  const getIcon = (mimeType: string) => {
    if (mimeType.startsWith('text/') || mimeType.includes('json') || mimeType.includes('xml')) {
      return <FileText className="h-4 w-4" />;
    }
    if (mimeType.startsWith('image/')) {
      return <Image className="h-4 w-4" />;
    }
    return <File className="h-4 w-4" />;
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
  };

  const getHashPrefix = (hash: string) => {
    return hash.substring(0, 8);
  };

  if (isLoading) {
    return <div className="text-center py-4">Loading snapshots...</div>;
  }

  if (snapshots.length === 0) {
    return <div className="text-center py-4 text-muted-foreground">No snapshots yet</div>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Type</TableHead>
          <TableHead>Created</TableHead>
          <TableHead>Size</TableHead>
          <TableHead>Hash</TableHead>
          <TableHead>Compression</TableHead>
          <TableHead>Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {snapshots.map((snapshot) => (
          <TableRow key={snapshot.id}>
            <TableCell className="flex items-center gap-2">
              {getIcon(snapshot.mime_type)}
              <span className="text-sm">{snapshot.mime_type}</span>
            </TableCell>
            <TableCell>
              {format(new Date(snapshot.created_at), 'MMM dd, yyyy HH:mm')}
            </TableCell>
            <TableCell>
              <div className="text-sm">
                <div>{formatSize(snapshot.size_compressed)}</div>
                <div className="text-muted-foreground">
                  {snapshot.size_compressed !== snapshot.size_original && 
                    `(${formatSize(snapshot.size_original)} original)`}
                </div>
              </div>
            </TableCell>
            <TableCell>
              <code className="text-xs bg-muted px-1 py-0.5 rounded">
                {getHashPrefix(snapshot.content_hash)}
              </code>
            </TableCell>
            <TableCell>
              <span className="text-sm capitalize">{snapshot.compression}</span>
            </TableCell>
            <TableCell>
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => viewSnapshot(snapshot.id)}
                  title="View snapshot"
                >
                  <Eye className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => downloadSnapshot(snapshot.id, `snapshot-${snapshot.id}`)}
                  title="Download snapshot"
                >
                  <Download className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => deleteSnapshot(snapshot.id)}
                  title="Delete snapshot"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
} 
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SnapshotViewer } from '@/components/snapshots/SnapshotViewer';
import { toast } from 'sonner';

interface SnapshotData {
  id: number;
  mime_type: string;
  size_original: number;
  size_compressed: number;
  compression: string;
  created_at: string;
}

export function SnapshotViewerPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [snapshot, setSnapshot] = useState<SnapshotData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchSnapshotData();
    }
  }, [id]);

  const fetchSnapshotData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch(`/api/snapshots/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Snapshot not found');
        }
        throw new Error('Failed to load snapshot');
      }

      const data = await response.json();
      setSnapshot(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load snapshot';
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    navigate(-1);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading snapshot...</p>
        </div>
      </div>
    );
  }

  if (error || !snapshot) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-destructive mb-4">{error || 'Snapshot not found'}</p>
          <Button onClick={handleClose} variant="outline">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Go Back
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Top bar */}
      <div className="flex items-center justify-between p-4 border-b bg-background">
        <Button onClick={handleClose} variant="ghost" size="sm">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <div className="text-sm text-muted-foreground">
          Snapshot #{snapshot.id} • {new Date(snapshot.created_at).toLocaleDateString()}
        </div>
      </div>

      {/* Viewer */}
      <div className="flex-1">
        <SnapshotViewer
          snapshotId={snapshot.id}
          mimeType={snapshot.mime_type}
          size={snapshot.size_compressed}
          compression={snapshot.compression}
        />
      </div>
    </div>
  );
} 
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Camera, ChevronDown, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

interface SnapshotButtonProps {
  linkId: number;
  onSnapshotCreated?: () => void;
  force?: boolean;
}

const compressionOptions = [
  { value: 'none', label: 'No Compression' },
  { value: 'gzip', label: 'Gzip' },
  { value: 'zstd', label: 'Zstandard' },
];

export function SnapshotButton({ linkId, onSnapshotCreated, force = false }: SnapshotButtonProps) {
  const [isLoading, setIsLoading] = useState(false);

  const takeSnapshot = async (compression: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/links/${linkId}/snapshot`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ compression, force }),
      });

      if (response.status === 208) {
        // Duplicate content detected
        const snapshot = await response.json();
        const contentHash = response.headers.get('X-Content-Hash');
        const hashPrefix = contentHash ? contentHash.substring(0, 8) : 'unknown';
        toast.info(`No change—latest snapshot already identical (sha256: ${hashPrefix})`);
        onSnapshotCreated?.();
        return;
      }

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create snapshot');
      }

      const snapshot = await response.json();
      toast.success(`Snapshot created successfully! Size: ${(snapshot.size_compressed / 1024).toFixed(1)}KB`);
      onSnapshotCreated?.();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to create snapshot');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button disabled={isLoading} variant="outline" size="sm">
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Camera className="h-4 w-4" />
          )}
          Take Snapshot
          <ChevronDown className="h-4 w-4 ml-1" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {compressionOptions.map((option) => (
          <DropdownMenuItem
            key={option.value}
            onClick={() => takeSnapshot(option.value)}
            disabled={isLoading}
          >
            {option.label}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
} 
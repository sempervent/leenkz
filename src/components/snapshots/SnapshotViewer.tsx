import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import DOMPurify from 'dompurify';
import { Download, FileText, Image, File, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

interface SnapshotViewerProps {
  snapshotId: number;
  mimeType: string;
  size: number;
  compression: string;
  onClose?: () => void;
}

interface SnapshotMetadata {
  id: number;
  mime_type: string;
  size_original: number;
  size_compressed: number;
  compression: string;
  created_at: string;
}

export function SnapshotViewer({ 
  snapshotId, 
  mimeType, 
  size, 
  compression, 
  onClose 
}: SnapshotViewerProps) {
  const [content, setContent] = useState<string | null>(null);
  const [blobUrl, setBlobUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<SnapshotMetadata | null>(null);

  useEffect(() => {
    fetchSnapshotContent();
    return () => {
      // Cleanup blob URL
      if (blobUrl) {
        URL.revokeObjectURL(blobUrl);
      }
    };
  }, [snapshotId]);

  const fetchSnapshotContent = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch(`/api/snapshots/${snapshotId}/render`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.status === 415) {
        // Not renderable, trigger download instead
        downloadSnapshot();
        return;
      }

      if (!response.ok) {
        throw new Error(`Failed to fetch snapshot: ${response.statusText}`);
      }

      // Get metadata from headers
      const metadata: SnapshotMetadata = {
        id: parseInt(response.headers.get('X-Snapshot-Id') || '0'),
        mime_type: response.headers.get('Content-Type') || mimeType,
        size_original: parseInt(response.headers.get('X-Original-Size') || '0'),
        size_compressed: size,
        compression: response.headers.get('X-Leenkz-Compression') || compression,
        created_at: response.headers.get('Last-Modified') || new Date().toISOString(),
      };
      setMetadata(metadata);

      if (mimeType.startsWith('image/')) {
        // Handle images
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setBlobUrl(url);
      } else {
        // Handle text content
        const text = await response.text();
        setContent(text);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load snapshot');
      toast.error('Failed to load snapshot content');
    } finally {
      setIsLoading(false);
    }
  };

  const downloadSnapshot = async () => {
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
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `snapshot-${snapshotId}`;
      document.body.appendChild(a);
      a.click();
      URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('Snapshot downloaded successfully');
    } catch (err) {
      toast.error('Failed to download snapshot');
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
  };

  const getMimeTypeIcon = (mime: string) => {
    if (mime.startsWith('text/') || mime.includes('json') || mime.includes('xml')) {
      return <FileText className="h-4 w-4" />;
    }
    if (mime.startsWith('image/')) {
      return <Image className="h-4 w-4" />;
    }
    return <File className="h-4 w-4" />;
  };

  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
            <p className="text-destructive mb-4">{error}</p>
            <Button onClick={downloadSnapshot} variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Download Instead
            </Button>
          </div>
        </div>
      );
    }

    if (mimeType.startsWith('image/') && blobUrl) {
      return (
        <div className="flex items-center justify-center min-h-64">
          <img 
            src={blobUrl} 
            alt="Snapshot content" 
            className="max-w-full max-h-full object-contain rounded-lg shadow-lg"
          />
        </div>
      );
    }

    if (content) {
      switch (mimeType) {
        case 'text/html':
          const sanitizedHtml = DOMPurify.sanitize(content);
          return (
            <iframe 
              srcDoc={sanitizedHtml} 
              className="w-full h-full border-0 rounded-lg"
              title="Snapshot HTML content"
            />
          );
        
        case 'text/markdown':
          return (
            <div className="prose prose-sm max-w-none dark:prose-invert p-6">
              <ReactMarkdown>{content}</ReactMarkdown>
            </div>
          );
        
        case 'text/plain':
        case 'text/css':
        case 'text/javascript':
        case 'application/json':
        case 'application/xml':
        case 'text/xml':
          return (
            <pre className="whitespace-pre-wrap text-sm p-6 bg-muted rounded-lg overflow-auto max-h-96">
              {content}
            </pre>
          );
        
        default:
          return (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <File className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground mb-4">
                  This content type cannot be previewed
                </p>
                <Button onClick={downloadSnapshot} variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Download Content
                </Button>
              </div>
            </div>
          );
      }
    }

    return null;
  };

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-card">
        <div className="flex items-center gap-3">
          {getMimeTypeIcon(mimeType)}
          <div>
            <h2 className="text-lg font-semibold">Snapshot Viewer</h2>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Badge variant="secondary">{mimeType}</Badge>
              <span>•</span>
              <span>{formatSize(size)}</span>
              {compression !== 'none' && (
                <>
                  <span>•</span>
                  <Badge variant="outline">{compression}</Badge>
                </>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Button onClick={downloadSnapshot} variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Download
          </Button>
          {onClose && (
            <Button onClick={onClose} variant="ghost" size="sm">
              Close
            </Button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {renderContent()}
      </div>
    </div>
  );
} 
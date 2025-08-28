import React, { useState, useEffect } from 'react';
import { Button, Alert, Spinner } from '@cloudscape-design/components';
import { getProxyUrl, createBlobUrl } from '../utils/fileProxy';

/**
 * Component to display files from S3 without CORS issues
 */
export default function FileViewer({ s3Url, token, fileName }) {
  const [blobUrl, setBlobUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadFile = async () => {
    if (!s3Url || !token) return;

    setLoading(true);
    setError(null);

    try {
      const url = await createBlobUrl(s3Url, token);
      setBlobUrl(url);
    } catch (err) {
      setError(`Failed to load file: ${err.message}`);
      console.error('Error loading file:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFile();
    
    // Cleanup blob URL when component unmounts
    return () => {
      if (blobUrl) {
        URL.revokeObjectURL(blobUrl);
      }
    };
  }, [s3Url, token]);

  const handleDownload = () => {
    if (blobUrl) {
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = fileName || 'download';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleView = () => {
    if (blobUrl) {
      window.open(blobUrl, '_blank');
    }
  };

  if (loading) {
    return <Spinner size="normal" />;
  }

  if (error) {
    return (
      <Alert
        statusIconAriaLabel="Error"
        type="error"
        header="File Load Error"
        action={
          <Button onClick={loadFile}>
            Retry
          </Button>
        }
      >
        {error}
      </Alert>
    );
  }

  if (!blobUrl) {
    return null;
  }

  return (
    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
      <Button onClick={handleView} variant="primary">
        View File
      </Button>
      <Button onClick={handleDownload}>
        Download
      </Button>
      <span style={{ fontSize: '14px', color: '#666' }}>
        {fileName || 'File'}
      </span>
    </div>
  );
}

/**
 * Simple component to create a direct link using the proxy
 */
export function FileLink({ s3Url, token, children, fileName }) {
  const [proxyUrl, setProxyUrl] = useState(null);

  useEffect(() => {
    if (s3Url && token) {
      const url = getProxyUrl(s3Url, token);
      setProxyUrl(url);
    }
  }, [s3Url, token]);

  if (!proxyUrl) {
    return <span>{children || fileName || 'Loading...'}</span>;
  }

  return (
    <a 
      href={proxyUrl} 
      target="_blank" 
      rel="noopener noreferrer"
      style={{ textDecoration: 'none' }}
    >
      {children || fileName || 'View File'}
    </a>
  );
}
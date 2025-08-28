import { API_ENDPOINT } from "../common/constants";

/**
 * Convert S3 URL to use the file proxy endpoint to avoid CORS issues
 * @param {string} s3Url - The S3 URL (either direct URL or presigned URL)
 * @param {object} token - Authentication token
 * @returns {string} - Proxy URL that can be used without CORS issues
 */
export function getProxyUrl(s3Url, token) {
  try {
    // Extract bucket and key from S3 URL
    const url = new URL(s3Url);
    
    // Handle different S3 URL formats
    let bucket, key;
    
    if (url.hostname.includes('.s3.')) {
      // Format: https://bucket.s3.region.amazonaws.com/key
      bucket = url.hostname.split('.')[0];
      key = url.pathname.substring(1); // Remove leading slash
    } else if (url.hostname === 's3.amazonaws.com') {
      // Format: https://s3.amazonaws.com/bucket/key
      const pathParts = url.pathname.substring(1).split('/');
      bucket = pathParts[0];
      key = pathParts.slice(1).join('/');
    } else {
      // Fallback: try to extract from pathname
      const pathParts = url.pathname.substring(1).split('/');
      bucket = pathParts[0];
      key = pathParts.slice(1).join('/');
    }
    
    // Build proxy URL
    const proxyUrl = `${API_ENDPOINT}/file-proxy?key=${encodeURIComponent(key)}&bucket=${encodeURIComponent(bucket)}`;
    
    console.log(`Converting S3 URL to proxy: ${s3Url} -> ${proxyUrl}`);
    
    return proxyUrl;
    
  } catch (error) {
    console.error('Error converting S3 URL to proxy URL:', error);
    return s3Url; // Fallback to original URL
  }
}

/**
 * Fetch file content through the proxy
 * @param {string} s3Url - The S3 URL
 * @param {object} token - Authentication token
 * @returns {Promise<Response>} - Fetch response
 */
export async function fetchFileViaProxy(s3Url, token) {
  const proxyUrl = getProxyUrl(s3Url, token);
  
  const headers = {
    'Authorization': token.token,
    'Content-Type': 'application/json',
  };
  
  try {
    const response = await fetch(proxyUrl, {
      method: 'GET',
      headers: headers,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response;
    
  } catch (error) {
    console.error('Error fetching file via proxy:', error);
    throw error;
  }
}

/**
 * Create a blob URL for file display/download
 * @param {string} s3Url - The S3 URL
 * @param {object} token - Authentication token
 * @returns {Promise<string>} - Blob URL
 */
export async function createBlobUrl(s3Url, token) {
  try {
    const response = await fetchFileViaProxy(s3Url, token);
    const blob = await response.blob();
    return URL.createObjectURL(blob);
  } catch (error) {
    console.error('Error creating blob URL:', error);
    throw error;
  }
}
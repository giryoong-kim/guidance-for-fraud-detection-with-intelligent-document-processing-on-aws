# Deploy File Proxy to Fix CORS Issues

## Problem
Your frontend is getting CORS errors when trying to access S3 files directly:
```
Cross-Origin Request Blocked: The Same Origin Policy disallows reading the remote resource... 
(Reason: CORS header 'Access-Control-Allow-Origin' missing)
```

## Solution
I've created a file proxy endpoint that serves S3 files through your API Gateway, avoiding CORS issues entirely.

## Files Created/Modified

### 1. Lambda Function
- **File**: `insurance_claim_process_cdk/lambdas/file_proxy/app.py`
- **Purpose**: Proxy Lambda that fetches files from S3 and serves them with proper CORS headers

### 2. CDK Stack Updates
- **File**: `insurance_claim_process_cdk/lambdafn.py` 
- **Changes**: Added file proxy Lambda function with S3 permissions

### 3. API Gateway Updates
- **File**: `insurance_claim_process_cdk/api.py`
- **Changes**: Added `/file-proxy` endpoint

### 4. Frontend Utilities
- **File**: `frontend/src/utils/fileProxy.js`
- **Purpose**: Helper functions to convert S3 URLs to proxy URLs

### 5. React Components
- **File**: `frontend/src/components/FileViewer.js`
- **Purpose**: Components to display/download files without CORS issues

## Deployment Steps

### 1. Deploy the Backend Changes
```bash
# Deploy the updated Lambda functions
cdk deploy InsuranceClaimProcessStack/InsuranceClaimProcessWorkflow

# Deploy the updated API
cdk deploy InsuranceClaimProcessStack/InsuranceClaimProcessApi
```

### 2. Test the File Proxy
After deployment, you can test the file proxy endpoint:
```
GET https://your-api-gateway-url/dev/file-proxy?key=demo-run-0001/Homeowners%20Insurance%20Policy.pdf&bucket=insuranceclaim-input-186297945978-us-east-1
```

### 3. Update Frontend Code
Instead of using S3 URLs directly, use the proxy utilities:

```javascript
import { getProxyUrl, createBlobUrl } from '../utils/fileProxy';
import FileViewer from '../components/FileViewer';

// Convert S3 URL to proxy URL
const proxyUrl = getProxyUrl(s3Url, token);

// Or use the FileViewer component
<FileViewer 
  s3Url="s3://bucket/key/file.pdf" 
  token={token} 
  fileName="document.pdf" 
/>
```

## How It Works

1. **Frontend** makes request to `/dev/file-proxy?key=path/to/file.pdf`
2. **API Gateway** routes to the file proxy Lambda
3. **Lambda** fetches file from S3 and returns it with CORS headers
4. **Frontend** receives file without CORS issues

## Benefits

- ✅ **No CORS issues** - Files served through your API domain
- ✅ **Authentication** - Uses your existing Cognito auth
- ✅ **Secure** - No direct S3 access needed from frontend
- ✅ **Flexible** - Works with any file type (PDF, images, etc.)

## API Endpoint

**URL**: `GET /file-proxy`

**Parameters**:
- `key` (required): S3 object key (path to file)
- `bucket` (optional): S3 bucket name (defaults to input bucket)

**Headers**:
- `Authorization`: Your Cognito JWT token

**Example**:
```
GET /dev/file-proxy?key=demo-run-0001/Homeowners%20Insurance%20Policy.pdf
Authorization: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Next Steps

1. Deploy the backend changes
2. Test the file proxy endpoint
3. Update your frontend components to use the proxy utilities
4. Remove any direct S3 URL usage from your frontend

This solution completely eliminates CORS issues while maintaining security and authentication!
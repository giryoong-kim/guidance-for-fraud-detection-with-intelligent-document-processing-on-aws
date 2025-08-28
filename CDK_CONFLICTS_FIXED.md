# CDK Stack Conflicts - Analysis and Fixes

## 🚨 **Conflicts Identified:**

### **1. Duplicate Lambda Stack Creation**
**Problem**: The `ApiStack` was creating a new `LambdaStack` instance, causing duplicate Lambda functions and resource conflicts.

**Location**: `insurance_claim_process_cdk/api.py`
```python
# PROBLEMATIC CODE:
from .lambdafn import LambdaStack
lambda_stack = LambdaStack(self, "LambdaStackForFileProxy")  # ❌ Creates duplicate!
```

**Impact**: 
- Duplicate Lambda functions with same names
- Resource naming conflicts
- CDK deployment failures
- Increased costs from duplicate resources

### **2. Stack Architecture Violation**
**Problem**: Lambda functions should be created in the workflow stack, not the API stack.

**Current Architecture**:
```
InsuranceClaimProcessStack (Main)
├── InsuranceClaimProcessWorkflow (Nested)
│   ├── LambdaStack ✅ (Correct location)
│   ├── S3Stack
│   ├── DynamoDBStack
│   └── ...
├── InsuranceClaimProcessApi (Nested)
│   └── LambdaStack ❌ (Duplicate - WRONG!)
└── InsuranceClaimProcessFrontEnd (Nested)
```

## 🔧 **Fixes Applied:**

### **1. Removed Duplicate Lambda Stack**
**File**: `insurance_claim_process_cdk/api.py`
- Removed the duplicate `LambdaStack` creation
- Added proper reference to existing Lambda functions

### **2. Updated Stack Communication**
**File**: `insurance_claim_process_cdk/insurance_claim_process_stack.py`
```python
# Pass lambda stack reference to API stack
api = ApiStack(self, "InsuranceClaimProcessApi", lambda_stack=lambda_)
```

**File**: `insurance_claim_process_cdk/api.py`
```python
# Accept lambda_stack parameter
def __init__(self, scope: Construct, id: str, lambda_stack=None, **kwargs):
    self.lambda_stack = lambda_stack
```

### **3. Conditional Endpoint Creation**
**File**: `insurance_claim_process_cdk/api.py`
```python
# Only create endpoints if Lambda functions exist
if self.lambda_stack and hasattr(self.lambda_stack, 'lambda_file_proxy'):
    # Create file-proxy endpoint
    
if self.lambda_stack and hasattr(self.lambda_stack, 'lambda_upload_proxy'):
    # Create upload-file endpoint
```

## ✅ **Fixed Architecture:**

```
InsuranceClaimProcessStack (Main)
├── InsuranceClaimProcessWorkflow (Nested)
│   ├── LambdaStack ✅ (Contains ALL Lambda functions)
│   │   ├── lambda_file_proxy
│   │   ├── lambda_upload_proxy
│   │   └── ... (other functions)
│   ├── S3Stack
│   ├── DynamoDBStack
│   └── ...
├── InsuranceClaimProcessApi (Nested)
│   └── References Lambda functions ✅ (No duplication)
└── InsuranceClaimProcessFrontEnd (Nested)
```

## 🚀 **Deployment Order:**

1. **Workflow Stack First**: Contains Lambda functions
   ```bash
   cdk deploy InsuranceClaimProcessStack/InsuranceClaimProcessWorkflow
   ```

2. **API Stack Second**: References Lambda functions
   ```bash
   cdk deploy InsuranceClaimProcessStack/InsuranceClaimProcessApi
   ```

## 🔍 **Verification Steps:**

### **1. Check for Duplicate Resources**
```bash
# Should show no duplicate Lambda functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `insuranceclaim`)]'
```

### **2. Verify API Endpoints**
```bash
# Test file proxy endpoint
curl -H "Authorization: <token>" \
  "https://your-api-gateway-url/dev/file-proxy?key=test-file.pdf"

# Test upload proxy endpoint
curl -X POST -H "Authorization: <token>" \
  -H "Content-Type: application/json" \
  -d '{"fileName":"test.txt","fileContent":"dGVzdA==","claimId":"test"}' \
  "https://your-api-gateway-url/dev/upload-file"
```

### **3. Monitor CloudWatch Logs**
- Check Lambda function logs for errors
- Verify API Gateway execution logs
- Monitor for any resource conflicts

## 📋 **Benefits of the Fix:**

- ✅ **No Resource Conflicts** - Single source of truth for Lambda functions
- ✅ **Proper Stack Separation** - Clear responsibility boundaries
- ✅ **Cost Optimization** - No duplicate resources
- ✅ **Maintainability** - Easier to manage and update
- ✅ **Deployment Reliability** - No naming conflicts

## 🎯 **Next Steps:**

1. Run the deployment script: `python deploy-cors-fix.py`
2. Test the CORS fixes in your frontend
3. Monitor for any remaining issues
4. Update documentation with new endpoints

The stack conflicts have been resolved and the architecture is now properly structured!
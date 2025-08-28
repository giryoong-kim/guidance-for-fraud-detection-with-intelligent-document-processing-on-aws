import boto3
import json
import base64
import os

def lambda_handler(event, context):
    """
    Proxy endpoint for file uploads to S3, avoiding CORS issues.
    Accepts JSON payload with base64-encoded file content.
    """
    
    # Handle CORS preflight requests
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': ''
        }
    
    try:
        # Parse JSON body
        body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body).decode('utf-8')
        
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({'error': 'Invalid JSON payload'})
            }
        
        # Extract required fields
        file_name = payload.get('fileName')
        file_content_b64 = payload.get('fileContent')
        claim_id = payload.get('claimId')
        content_type = payload.get('contentType', 'application/octet-stream')
        
        if not all([file_name, file_content_b64, claim_id]):
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({'error': 'Missing required fields: fileName, fileContent, claimId'})
            }
        
        # Decode base64 file content
        try:
            file_content = base64.b64decode(file_content_b64)
        except Exception as e:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({'error': f'Invalid base64 file content: {str(e)}'})
            }
        
        # Create S3 key
        key = f"{claim_id}/{file_name}"
        
        # Get S3 bucket
        account_id = context.invoked_function_arn.split(':')[4]
        region = os.environ.get('AWS_REGION', 'us-east-1')
        bucket = f'insuranceclaim-input-{account_id}-{region}'
        
        print(f"Uploading file to s3://{bucket}/{key} (size: {len(file_content)} bytes)")
        
        # Upload to S3
        s3_client = boto3.client('s3')
        
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=file_content,
            ContentType=content_type
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'message': 'File uploaded successfully via proxy',
                'bucket': bucket,
                'key': key,
                'fileName': file_name,
                'size': len(file_content)
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }
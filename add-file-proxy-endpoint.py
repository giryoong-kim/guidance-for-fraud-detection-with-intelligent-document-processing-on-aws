#!/usr/bin/env python3
"""
Lambda function code for a file proxy endpoint to avoid CORS issues.
Add this as a new Lambda function in your CDK stack.
"""

import boto3
import json
import base64
from urllib.parse import unquote

def lambda_handler(event, context):
    """
    Proxy endpoint to serve S3 files through API Gateway, avoiding CORS issues.
    """
    
    try:
        # Get the S3 key from query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        s3_key = query_params.get('key')
        bucket = query_params.get('bucket')
        
        if not s3_key or not bucket:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'GET,OPTIONS'
                },
                'body': json.dumps({'error': 'Missing key or bucket parameter'})
            }
        
        # Decode URL-encoded key
        s3_key = unquote(s3_key)
        
        # Initialize S3 client
        s3_client = boto3.client('s3')
        
        # Get the file from S3
        response = s3_client.get_object(Bucket=bucket, Key=s3_key)
        file_content = response['Body'].read()
        
        # Determine content type
        content_type = response.get('ContentType', 'application/octet-stream')
        
        # For binary files, encode as base64
        is_binary = not content_type.startswith('text/') and content_type != 'application/json'
        
        if is_binary:
            body = base64.b64encode(file_content).decode('utf-8')
            is_base64_encoded = True
        else:
            body = file_content.decode('utf-8')
            is_base64_encoded = False
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': content_type,
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,OPTIONS',
                'Content-Disposition': f'inline; filename="{s3_key.split("/")[-1]}"'
            },
            'body': body,
            'isBase64Encoded': is_base64_encoded
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }

# For OPTIONS requests (CORS preflight)
def handle_options():
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        },
        'body': ''
    }
#!/usr/bin/env python3
"""
Script to configure CORS on S3 buckets for the insurance claims application.
"""

import boto3
import json

def configure_s3_cors():
    """Configure CORS on S3 buckets to allow frontend access."""
    
    s3_client = boto3.client('s3')
    
    # List of buckets to configure
    buckets = [
        'insuranceclaim-input-186297945978-us-east-1',
        'insuranceclaim-output-186297945978-us-east-1'
    ]
    
    # Enhanced CORS configuration
    cors_configuration = {
        'CORSRules': [
            {
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD', 'OPTIONS'],
                'AllowedOrigins': [
                    '*'  # Allow all origins for development - restrict in production
                ],
                'ExposeHeaders': [
                    'ETag',
                    'x-amz-meta-custom-header',
                    'x-amz-version-id',
                    'x-amz-request-id',
                    'x-amz-id-2',
                    'Access-Control-Allow-Origin',
                    'Access-Control-Allow-Methods',
                    'Access-Control-Allow-Headers'
                ],
                'MaxAgeSeconds': 86400  # 24 hours
            }
        ]
    }
    
    for bucket_name in buckets:
        try:
            print(f"🔧 Configuring CORS for bucket: {bucket_name}")
            
            # Check if bucket exists
            try:
                s3_client.head_bucket(Bucket=bucket_name)
            except s3_client.exceptions.NoSuchBucket:
                print(f"⚠️  Bucket {bucket_name} does not exist. Skipping...")
                continue
            
            # Apply CORS configuration
            s3_client.put_bucket_cors(
                Bucket=bucket_name,
                CORSConfiguration=cors_configuration
            )
            
            print(f"✅ CORS configured successfully for {bucket_name}")
            
            # Verify the configuration
            response = s3_client.get_bucket_cors(Bucket=bucket_name)
            print(f"📋 Current CORS rules for {bucket_name}:")
            print(json.dumps(response['CORSRules'], indent=2))
            
        except Exception as e:
            print(f"❌ Error configuring CORS for {bucket_name}: {str(e)}")

if __name__ == "__main__":
    print("🏥 S3 CORS Configuration for Insurance Claims App")
    print("=" * 60)
    configure_s3_cors()
    print("\n✅ CORS configuration completed!")
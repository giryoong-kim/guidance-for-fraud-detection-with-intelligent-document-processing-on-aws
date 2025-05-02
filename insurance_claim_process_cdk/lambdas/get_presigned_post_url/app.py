import boto3
import os
import random
import json

# Initialize S3 client
s3_client = boto3.client('s3',
    region_name=os.environ.get('AWS_REGION')
)

UPLOAD_BUCKET = os.environ.get('INPUT_BUCKET')  # Replace this value with your bucket name!
URL_EXPIRATION_SECONDS = 300     # Specify how long the pre-signed URL will be valid for

def lambda_handler(event, context):
    file_name = event['queryStringParameters']['file']
    claim_id = event['queryStringParameters']['claim_id']
    # Generate a random filename
    key = f"{claim_id}/{file_name}"  # Random filename we will use when uploading files
    
    # Parameters for the pre-signed URL
    s3_params = {
        'Bucket': UPLOAD_BUCKET,
        'Key': key,
        'ContentType': 'application/octet-stream',
        'Expires': URL_EXPIRATION_SECONDS
    }
    
    try:
        # Generate the presigned URL
        upload_url = s3_client.generate_presigned_url(
            ClientMethod='put_object',
            Params=s3_params
        )
        
        # Prepare the response
        response = {
            "statusCode": 200,
            "isBase64Encoded": False,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "uploadURL": upload_url,
                "filename": key
            })
        }
        
        return response
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
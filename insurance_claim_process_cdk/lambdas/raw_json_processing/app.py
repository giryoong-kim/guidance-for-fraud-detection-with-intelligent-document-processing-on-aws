"""
A Lambda code which finds all the results.json files in S3 location, read them and store in DynamoDB
"""

import json
import boto3
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
from decimal import Decimal

def get_json_files(bucket_name, key):

    response = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=key
    )
    files = [obj['Key'] for obj in response.get('Contents', []) if "custom_output" in obj["Key"] and "result.json" in obj["Key"]]
    if not (len(files)):
        files =  [obj['Key'] for obj in response.get('Contents', []) if  "result.json" in obj["Key"]]
    return files

def read_json_from_s3(bucket_name, file_key, source_key, claim_id):

    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    content = response['Body'].read().decode('utf-8')
    json_content = json.loads(content, parse_float=Decimal)
    
    return {"claimId": claim_id, "name": source_key.split("/")[-1], "documentType": json_content.get("matched_blueprint", {"name": "Others"})["name"], **json_content}

def lambda_handler(event, context):

    bucket_name = event['outputBucket']
    claim_id = event['claimId']
    source_key = event["key"]
    dynamodb_table = "insuranceclaim-bda-results-raw"
    
    # Get all results.json files
    json_files = get_json_files(bucket_name, source_key)

    # Read and store. Assume there will be only one result.json
    file_key = json_files[0]
    print(file_key)
    data = read_json_from_s3(bucket_name, file_key, source_key, claim_id)
    #print(data)
    dynamodb.Table(dynamodb_table).put_item(Item=data)
    documentType = data["documentType"]
    name = data["name"]
    return {'statusCode': 200, "name":name, 'documentType': documentType}




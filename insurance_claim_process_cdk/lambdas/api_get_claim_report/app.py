"""
A lambda function which retrieves claim report from a dynamodb table insuranceclaim-reports-json using a partition key claimId
"""
import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('insuranceclaim-reports-json')

def lambda_handler(event, context):

    claim_id = event["queryStringParameters"]['claimId']
    response = table.get_item(Key={'claimId': claim_id})
    item = response['Item']
    return {
        'statusCode': 200,
        'body': json.dumps(item, default = str),
        'headers': {
            "Access-Control-Allow-Origin": "*", # Required for CORS support to work
            "Access-Control-Allow-Credentials": True, # Required for cookies, authorization headers with HTTPS
        },
    }
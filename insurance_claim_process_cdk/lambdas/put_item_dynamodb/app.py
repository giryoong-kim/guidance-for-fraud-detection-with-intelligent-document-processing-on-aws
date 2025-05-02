import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    table = dynamodb.Table(event["dynamodbTable"])
    body = event['body']
    body = json.loads(json.dumps(body), parse_float=Decimal)
    response = table.put_item(Item = body)
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

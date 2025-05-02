"""
A lambda function which retrieves claims from a dynamodb table insuranceclaim-reports-json
"""
import boto3
import json

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):

    table = dynamodb.Table('insuranceclaim-reports-json')
    response = table.scan(ProjectionExpression = 'claimId, claimInfo, incidentInfo')
    claims = response.get('Items', [])
    claims = [
        {
            "claimId":claim["claimId"],
            "claimFileDate":claim["claimInfo"].get("claimFiledDate", "Unknown"),
            "incidentDate":claim["incidentInfo"].get("date", "Unknown"),
            "description":claim["incidentInfo"].get("description", "Unknown")
        } for claim in claims
    ]
    print(claims)
    return {
        'statusCode': 200,
        'body': json.dumps(claims, default = str),
        'headers': {
            "Access-Control-Allow-Origin": "*", # Required for CORS support to work
            "Access-Control-Allow-Credentials": True, # Required for cookies, authorization headers with HTTPS
        },
    }
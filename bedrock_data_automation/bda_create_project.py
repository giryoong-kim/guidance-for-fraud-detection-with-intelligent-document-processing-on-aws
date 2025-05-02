import boto3
from bda_blueprints_create import create_bluprints
import os

PROJECT_NAME = "insurance-claim-process"
PROJECT_DESCRIPTION = "Insurance claim process automation project"
SCHEMA_FOLDER = "blueprints"
AWS_REGION = "us-east-1"

client = boto3.client('bedrock-data-automation', region_name=AWS_REGION)

blueprint_arns = create_bluprints(SCHEMA_FOLDER, region_name=AWS_REGION)

response = client.create_data_automation_project(
    projectName=PROJECT_NAME,
    projectDescription=PROJECT_DESCRIPTION,
    projectStage='LIVE',
    standardOutputConfiguration= {
            "audio": {
                "extraction": {
                    "category": {
                        "state": "ENABLED",
                        "types": [
                            "TRANSCRIPT"
                        ]
                    }
                },
                "generativeField": {
                    "state": "ENABLED",
                    "types": [
                        "AUDIO_SUMMARY"
                    ]
                }
            }
        },
    customOutputConfiguration={
        'blueprints': [
            {
                'blueprintArn': arn,
                "blueprintStage": "LIVE"
            } for arn in blueprint_arns
        ]
    },
)

print(response)
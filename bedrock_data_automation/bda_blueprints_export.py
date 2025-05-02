import boto3
import json

AWS_REGION = "us-east-1"

client = boto3.client('bedrock-data-automation', region_name=AWS_REGION)

# List blueprints
response = client.list_blueprints(
    maxResults=10
)

for blueprint in response["blueprints"]:
    print(blueprint["blueprintArn"])
    response_blueprint = client.get_blueprint(blueprintArn=blueprint["blueprintArn"])
    print(json.dumps(response_blueprint["blueprint"], indent=2, default=str))
    with open(f"blueprints/{response_blueprint['blueprint']['type']}/{blueprint['blueprintName']}.schema.json","w") as f:
        json.dump(json.loads(response_blueprint["blueprint"]["schema"]), f, indent=4, default=str)

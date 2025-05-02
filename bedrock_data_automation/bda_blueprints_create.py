import boto3
import json
import os


def create_bluprints(folder_name, region_name):
    client = boto3.client('bedrock-data-automation', region_name=region_name)
    arns = []
    # Iterate json files in bleprint/DOCUMENT folder
    for file in os.listdir(f"{folder_name}/DOCUMENT"):
        if file.endswith(".json"):
            with open(f"{folder_name}/DOCUMENT/{file}") as f:
                blueprint = json.load(f)
                response = client.create_blueprint(
                    blueprintName=file.split(".")[0],
                    type='DOCUMENT',
                    schema=json.dumps(blueprint)
                )
                arns.append(response["blueprint"]['blueprintArn'])

    # Iterate json files in bleprint/IMAGE folder
    for file in os.listdir(f"{folder_name}/IMAGE"):
        if file.endswith(".json"):
            with open(f"{folder_name}/IMAGE/{file}") as f:
                blueprint = json.load(f)
                response = client.create_blueprint(
                    blueprintName=file.split(".")[0],
                    type='IMAGE',
                    schema=json.dumps(blueprint)
                )
                arns.append(response["blueprint"]['blueprintArn'])
    return arns

if __name__ == "__main__":
    arns = create_bluprints("blueprints")
    print(arns)
import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb_raw_table = "insuranceclaim-bda-results-raw"

def lambda_handler(event, context):
    claim_id = event["claimId"]

    raw = read_items_from_dynamodb(dynamodb_raw_table, claim_id)
    print(len(raw))
    cleansed = cleanse(raw)

    messages = [ 
      { "Role": "user",
         "Content": [ 
            { 
                "Text": '```json\n' + json.dumps(cleansed,  default=str)+'\n```'
            }
         ]
      }
    ]
    system = [ 
      { 
        "Text": """Generate an output JSON by compiling input JSON given. Think throughly and compare all the given information to derive values in the JSON.
        Summarize and generate values based on the input. Especially, check if there is recorded audio from customer phone call which states difference facts than other documents. If you find contradicting information within the input, add it to "insights" attribute in the JSON. Include following attributes in the output JSON: 
        claimId: ID of the claim
        policyNo: Policy ID
        policyInfo: Insurnace company, agent name and contact. 
        callRecordingsSummary: Summary from customer call recorded in audio file.
        propertyInfo: Type of property. Address. Any additional info on the proprty.
        incidentInfo: Description of what happened and when.
        claimInfo: When a claim was filed. If a claimant signed properly. Estimated cost of repair and estimated value of damage that were claimed.
        witness: State if any witness exists and they signed the document properly.
        policyHolderDetails: Name,address and other details related to the policy holder
        descriptionOfDamage: Summary of the descriptions on the damage provided including inferenced descriptions from picutures provided.
        proofOfDamage: List of the proof of damages. Statement of validity check if the proof was tampered and its description matches claim info.
        estimatesOfTotalCostToRepairPerEachVendor: Total cost of repair, scope of work per an each vendor
        observations: Statement if this claim seems valid one. If there is any contradicting information, state them as potential fraud. State any suspicious points.
        insights: Based on the input and observations, key factors of this claim
        fraudWarning: True or False. If there was any sign of fraud detected based on the observations.
        suspicion: State which parts were suspicious in this claim.
        """
      }
    ]
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': {
            "messages" : messages,
            "system" : system
        }
    }

def cleanse(raw):
    cleansed = {}
    for i in raw:
        print(i.keys())
        cleansed["claimId"] = i["claimId"]
        cleansed[i["name"]] = i["inference_result"] if i["documentType"] != "Others" else i["audio"]
        cleansed[i["name"]]["fraudWarning"] = i.get("fraudDetection", "None")
    return cleansed

def read_items_from_dynamodb(table_name, claim_id):
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    
    # Get the table
    table = dynamodb.Table(table_name)
    
    # Perform the query
    response = table.query(
        KeyConditionExpression=Key("claimId").eq(claim_id)
    )
    
    # Extract items from the response
    items = response['Items']
    
    return items
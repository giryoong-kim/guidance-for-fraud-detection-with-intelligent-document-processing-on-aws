import os
import logging

os.environ["BYPASS_TOOL_CONSENT"] = "true"

CLAIM_ID = "dev-usecase-01"

CONFIG = {
  "inputBucket": "insuranceclaim-input-670934798598-us-west-2",
  "outputBucket": "insuranceclaim-output-670934798598-us-west-2",
  "bdaProjectArn": "arn:aws:bedrock:us-west-2:670934798598:data-automation-project/37a1c412b824",
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SAMPLE_SFN_PAYLOAD = {
    "inputBucket": "insuranceclaim-input-670934798598-us-west-2",
    "outputBucket": "insuranceclaim-output-670934798598-us-west-2",
    "key": "dev-use-case-01/Description of Damage.pdf",
    "bdaProjectArn": "arn:aws:bedrock:us-west-2:670934798598:data-automation-project/37a1c412b824",
    "claimId": "dev-use-case-01"
}


#############

# Define a tool to invoke the ML model
from strands import Agent, tool
from strands_tools import use_aws, mem0_memory
from tampered_image_detection import check_image
import json
import time
import boto3
import os
from strands.models.bedrock import BedrockModel
from datetime import datetime


os.environ["BYPASS_TOOL_CONSENT"] = "true"

@tool
def invoke_bda_sfn(document_s3_key: str) -> str:
    """
    Execute BDA to extract or infer information from given files.
    Args:
    document_s3_key(str): A key path to the file, excluding s3 bucket name.
    """
    sfn = boto3.client('stepfunctions')
    dynamodb = boto3.resource('dynamodb')
    # Get the table
    table = dynamodb.Table('insuranceclaim-bda-results-raw')
    
    response = sfn.start_execution(
        stateMachineArn=f"arn:aws:states:us-west-2:670934798598:stateMachine:insuranceclaim-Ingestion",
        input=json.dumps({**SAMPLE_SFN_PAYLOAD, "key": document_s3_key})
    )

    # Get the execution ARN from the response
    execution_arn = response['executionArn']

    claim_id = document_s3_key.split('/')[0]
    document_name = document_s3_key.split('/')[1]

    while True:
        # Get execution status
        execution_response = sfn.describe_execution(
            executionArn=execution_arn
        )

        status = execution_response['status']

        if status in ['SUCCEEDED']:
            # Store the output to DynamoDB
            output_bucket = json.loads(execution_response["output"])["outputBucket"]
            output_key = json.loads(execution_response["output"])["outputKey"]
            input_bucket = json.loads(execution_response["output"])["inputBucket"]
            input_key = json.loads(execution_response["output"])["inputKey"]
            print(execution_response["output"])
            item = {
                'claimId': claim_id,
                'name': document_name,
                'inputBucket': input_bucket,
                'inputKey': input_key,
                'outputBucket': output_bucket,
                'outputKey': output_key,
                'timestamp': datetime.utcnow().isoformat(),
            }
            response = table.put_item(Item=item)
            print(f"Successfully added document {document_name} for claim {claim_id}")
            # Return the output from the state machine
            return status
        elif status in ['FAILED', 'TIMED_OUT', 'ABORTED']:
            return status
        # Wait for 5 seconds before checking again
        time.sleep(3)
    return "FAILED"

# Testing
#invoke_bda_sfn("dev-use-case-01/Description of Damage.pdf")

model = BedrockModel(model_id="anthropic.claude-3-5-haiku-20241022-v1:0")

document_processor_agent = Agent(
    name="document_processor",
    model=model,
    system_prompt=f"You are a document processor handling multi-modal documents including text, PDFs, images, audio and video files."
    f"You will be given with a CLAIM_ID."
    f"Firstly, scan a prefix in a S3 bucket {CONFIG['inputBucket']} and find keys for each document."
    f"Then run `invoke_bda_sfn` tool parallely to process the documents.",
    tools=[use_aws, invoke_bda_sfn]
    )

@tool
def document_processor(claim_id:str):
    """ A document processor extracting data from multi-modal documents including text, PDFs, images, audio and video files.
        The extracted results will be stored into a JSON file in S3.
        This function will store the location of the JSON file in a DyanmoDB table `insuranceclaim-bda-results-raw`
        Args:
            claim_id(str)
    """
    response = document_processor_agent(claim_id)
    return response.message["content"][0]["text"]


# Testing
#document_processor(CLAIM_ID)



######################
# Define a tool to invoke the ML model
from strands import Agent, tool
from tampered_image_detection import check_image


@tool
def detect_tampered_image(s3_uri: str) -> str:
    """
    Detect if the input image is a forged one or not.
    Args:
    s3_uri(str): A S3 URI to the image file.

    Return (str): "tampered" if the image is a forged one, "original" if not.
    """
    #logger.info(s3_uri)
    response = check_image(s3_uri, "document-tampering-detection-v-DEMO")
    
    return "tampered" if response else "original"
    
#detect_tampered_image( "s3://insuranceclaim-input-670934798598-us-west-2/dev-use-case-01/Proof-of-damage.png")
#tampered_image_detector_agent = Agent(system_prompt="You are a fraud detector for insurance claims document processing."
#              "Detect if given image files were forged one or not. Be concise about your answer, mentioning only if the image seems tampered one or not.",
#              tools = [detect_tampered_image])

#Testing
#response = detect_tampered_image(
#   "s3://insuranceclaim-input-670934798598-us-west-2/test/Noisy Image (Random)_screenshot_23.07.2025.png"
#)
#response


###########################
# Web search tool
from strands import tool, Agent
from ddgs import DDGS

@tool
def web_search(
    keywords: str,
    region: str = "us-en",
    max_results: int = 7,
) -> str:
    """Search the web to get updated information.
    Args:
        keywords (str): The search query keywords.
        region (str): The search region: wt-wt, us-en, uk-en, ru-ru, etc..
        max_results (int | None): The maximum number of results to return.
    Returns:
        List of dictionaries with search results.
    """
    try:
        results = DDGS().text(keywords, region=region, max_results=max_results)
        return results if results else "No results found."
    except Exception as e:
        return f"Exception: {e}"

# Test
#web_search("How much does it cost to fix a car")



#################

from strands_tools import think
from strands_tools import mem0_memory, use_aws, current_time, use_aws, python_repl


model = BedrockModel(model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0")

investigator_agent = Agent(
    name="investigator",
    model=model,
    system_prompt="You are an assistant for the inspector."
          "Find the extracted data from the claim, then check if the documents are truthful using tools provided."
          "You can find list of the documents by scanning a DynamoDB table `insuranceclaim-bda-results-raw` in us-west-2, using claimId as a key"
          "For example, use detect_tampered_image tool with S3 URI of  .png files to see if they are forged ones."
          "For stated facts, try your best to validate them by getting helps from the provided tool"
          "Store summary of documents and findings to a DynamoDB table insuranceclaim-reports-json in us-west-2, using claimId as a key"
          "State clearly, and point out which documents have suspicious points."
          "Use your memory to remember the key findings into memory, using the claim_id as agent_id",
    tools = [use_aws, detect_tampered_image, web_search, mem0_memory, current_time], )

#investigator_agent(CLAIM_ID)


###################################

from strands_tools import mem0_memory, use_aws, current_time, use_aws, python_repl, think


model = BedrockModel(model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0")

adjustor_agent = Agent(
    name="adjustor",
    model=model,
    system_prompt="You are an claim adjustor. Find policy document for the insurance case, and find out the fair and accurate payout for the claim, and suggest adjusted payout."
    "You can find list of the documents by scanning a DynamoDB table `insuranceclaim-bda-results-raw` in us-west-2, using claimId as a key"
    "You can find summary and findings on the claim from a DynamoDB table `insuranceclaim-reports-json` in us-west-2, using claimId as a key"
    "Use memory to check what investigator has found regarding the claim. Use claim_id as agent_id."
    "Generate your suggestion for adjusting the claim case, and remember your suggestion to memory, using claim_id as a user_id.",
    tools = [use_aws, mem0_memory], )


#Testing
#adjustor_agent(CLAIM_ID)

#########################

from strands_tools import think
from strands_tools import mem0_memory, use_aws, current_time, use_aws


model = BedrockModel(model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0")

report_agent = Agent(
    model=model,
    name="report",
    system_prompt="You are a insurnace claim agent.Combining the information, you generate a comprehensive report on the insurance claim."
    "The report should include summary of key information of the claim, claimant info and insights from the investigator and adjustor."
    "You can find list of the documents by scanning a DynamoDB table `insuranceclaim-bda-results-raw` in us-west-2, using claimId as a key"
    "Use memory to check what investigator has found regarding the claim. Use claim_id as agent_id."
    "Use memory to check what adjustor has suggested regarding the claim. Use claim_id as user_id."
    "Generate the final report in Markdown format."
    "Store the generated report to DynamoDB table insuranceclaim-reports-doc in us-west-2, using claimId as a key, `markdown` as an attribute",
    tools = [use_aws, mem0_memory])

#Testing
#report_agent(CLAIM_ID)


#############################

from strands_tools import mem0_memory, use_aws, current_time, use_aws, python_repl, think


model = BedrockModel(model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0")

reviewer_agent = Agent(
    name="reviwer",
    model=model,
    system_prompt="You are a reviwer of insurnace claim cases. "
    "A document is stored in DynamoDB table insuranceclaim-reports-doc in us-west-2. Retrive `markdown` attribute using claimId as a key."
    "Review the documents and find out if anything is missing. If so, send it back.",
    tools = [use_aws, mem0_memory, python_repl], )

#Testing
#reviewer_agent(CLAIM_ID)

from strands import Agent
from strands.multiagent import GraphBuilder, Swarm

builder = GraphBuilder()

builder.add_node(document_processor_agent, "document_processor")

builder.add_node(investigator_agent, "investigator")

builder.add_node(adjustor_agent, "adjustor")

builder.add_node(report_agent, "reporter")


builder.add_edge("document_processor", "investigator")
builder.add_edge("investigator", "adjustor")
builder.add_edge("adjustor", "reporter")

# Set entry points (optional - will be auto-detected if not specified)
builder.set_entry_point("document_processor")

# Build the graph
graph = builder.build()

#graph(CLAIM_ID)
#############
from bedrock_agentcore.runtime import BedrockAgentCoreApp
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    """Process user input and return a response"""
    response = graph(payload["claimId"])
    return {"result": response}

if __name__ == "__main__":
    app.run()
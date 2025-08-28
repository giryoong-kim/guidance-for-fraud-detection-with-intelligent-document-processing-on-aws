import os
import logging
from botocore.config import Config

config = Config(read_timeout=3600)

os.environ["BYPASS_TOOL_CONSENT"] = "true"

CLAIM_ID = "dev-use-case-local-run"  # For testing

CONFIG = {
    "inputBucket": "insuranceclaim-input-670934798598-us-east-1",
    "outputBucket": "insuranceclaim-output-670934798598-us-east-1",
    "bdaProjectArn": "arn:aws:bedrock:us-east-1:670934798598:data-automation-project/37a1c412b824",
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SAMPLE_SFN_PAYLOAD = {
    "inputBucket": "insuranceclaim-input-670934798598-us-east-1",
    "outputBucket": "insuranceclaim-output-670934798598-us-east-1",
    "key": "dev-use-case-01/Description of Damage.pdf",
    "bdaProjectArn": "arn:aws:bedrock:us-east-1:670934798598:data-automation-project/37a1c412b824",
    "claimId": "dev-use-case-01",
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
    Handles IMAGE modality blueprint limits gracefully.
    Args:
    document_s3_key(str): A key path to the file, excluding s3 bucket name.
    """
    sfn = boto3.client("stepfunctions", config=config)
    dynamodb = boto3.resource("dynamodb")
    # Get the table
    table = dynamodb.Table("insuranceclaim-bda-results-raw")

    claim_id = document_s3_key.split("/")[0]
    document_name = document_s3_key.split("/")[1]
    
    # Check if this is an image file
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']
    is_image = any(document_name.lower().endswith(ext) for ext in image_extensions)

    try:
        response = sfn.start_execution(
            stateMachineArn=f"arn:aws:states:us-east-1:670934798598:stateMachine:insuranceclaim-Ingestion",
            input=json.dumps({**SAMPLE_SFN_PAYLOAD, "key": document_s3_key}),
        )

        # Get the execution ARN from the response
        execution_arn = response["executionArn"]

        while True:
            # Get execution status
            execution_response = sfn.describe_execution(executionArn=execution_arn)

            status = execution_response["status"]

            if status in ["SUCCEEDED"]:
                # Store the output to DynamoDB
                output_bucket = json.loads(execution_response["output"])["outputBucket"]
                output_key = json.loads(execution_response["output"])["outputKey"]
                input_bucket = json.loads(execution_response["output"])["inputBucket"]
                input_key = json.loads(execution_response["output"])["inputKey"]
                print(execution_response["output"])
                item = {
                    "claimId": claim_id,
                    "name": document_name,
                    "inputBucket": input_bucket,
                    "inputKey": input_key,
                    "outputBucket": output_bucket,
                    "outputKey": output_key,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                response = table.put_item(Item=item)
                print(f"Successfully added document {document_name} for claim {claim_id}")
                return status
                
            elif status in ["FAILED", "TIMED_OUT", "ABORTED"]:
                # Check if failure is due to IMAGE blueprint limit
                error_details = ""
                if 'output' in execution_response and execution_response['output']:
                    try:
                        output = json.loads(execution_response['output'])
                        error_details = str(output)
                    except:
                        pass
                
                # Handle IMAGE blueprint limit
                if is_image and ("IMAGE modality" in error_details or "blueprint" in error_details.lower()):
                    print(f"⚠️  IMAGE blueprint limit exceeded for {document_name}. Skipping BDA processing.")
                    # Store minimal info indicating BDA was skipped
                    item = {
                        "claimId": claim_id,
                        "name": document_name,
                        "inputBucket": CONFIG["inputBucket"],
                        "inputKey": document_s3_key,
                        "outputBucket": "N/A",
                        "outputKey": "BDA_SKIPPED_IMAGE_LIMIT",
                        "timestamp": datetime.utcnow().isoformat(),
                        "status": "BDA_SKIPPED_IMAGE_LIMIT",
                        "note": "Image processing skipped due to BDA blueprint limit"
                    }
                    table.put_item(Item=item)
                    return "SKIPPED_IMAGE_LIMIT"
                
                print(f"❌ BDA processing failed for {document_name}: {status}")
                return status
                
            # Wait for 3 seconds before checking again
            time.sleep(3)
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error processing {document_name}: {error_msg}")
        
        # Handle IMAGE blueprint limit error at the API level
        if is_image and ("IMAGE modality" in error_msg or "blueprint" in error_msg.lower() or "limit" in error_msg.lower()):
            print(f"⚠️  IMAGE blueprint limit exceeded for {document_name}. Storing without BDA processing.")
            # Store minimal info indicating BDA was skipped
            item = {
                "claimId": claim_id,
                "name": document_name,
                "inputBucket": CONFIG["inputBucket"],
                "inputKey": document_s3_key,
                "outputBucket": "N/A",
                "outputKey": "BDA_SKIPPED_IMAGE_LIMIT",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "BDA_SKIPPED_IMAGE_LIMIT",
                "note": "Image processing skipped due to BDA blueprint limit"
            }
            table.put_item(Item=item)
            return "SKIPPED_IMAGE_LIMIT"
        
        return f"ERROR: {error_msg}"


# Testing
# invoke_bda_sfn("dev-use-case-01/Description of Damage.pdf")


model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0", boto_client_config=config
)

document_processor_agent = Agent(
    name="document_processor",
    model=model,
    system_prompt=f"You are a document processor handling multi-modal documents including text, PDFs, images, audio and video files."
    f"Use input string as a claim_id."
    f"Firstly, scan a prefix in a S3 bucket {CONFIG['inputBucket']} and find keys for each document."
    f"Then run `invoke_bda_sfn` tool parallely to process the documents.",
    tools=[use_aws, invoke_bda_sfn],
)

@tool
def document_processor(claim_id: str) -> str:
    """
    A document processor extracting data from multi-modal documents including text, PDFs, images, audio and video files.
    The extracted results will be stored into a JSON file in S3.
    This function will store the location of the JSON file in a DynamoDB table `insuranceclaim-bda-results-raw`

    Args:
        claim_id (str): The claim ID to process documents for

    Returns:
        str: Processing status and summary
    """


    response = document_processor_agent(claim_id)
    return response.message["content"][0]["text"]


# Testing
# document_processor(CLAIM_ID)


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
    # logger.info(s3_uri)
    response = check_image(s3_uri, "document-tampering-detection-v-DEMO")

    return "tampered" if response else "original"


# detect_tampered_image( "s3://insuranceclaim-input-670934798598-us-east-1/dev-use-case-01/Proof-of-damage.png")
# tampered_image_detector_agent = Agent(system_prompt="You are a fraud detector for insurance claims document processing."
#              "Detect if given image files were forged one or not. Be concise about your answer, mentioning only if the image seems tampered one or not.",
#              tools = [detect_tampered_image])

# Testing
# response = detect_tampered_image(
#   "s3://insuranceclaim-input-670934798598-us-east-1/test/Noisy Image (Random)_screenshot_23.07.2025.png"
# )
# response


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
# web_search("How much does it cost to fix a car")


#################

from strands_tools import think
from strands_tools import use_aws, current_time, use_aws, python_repl
model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    boto_client_config=config,
)

investigator_agent = Agent(
    name="investigator",
    model=model,
    system_prompt="You are an assistant for the inspector."
    "Use input string as a claim_id."
    "Find the extracted data from the claim, then check if the documents are truthful using tools provided."
    "You can find list of the documents by scanning a DynamoDB table `insuranceclaim-bda-results-raw` in us-east-1, using claimId as a key"
    "For example, use detect_tampered_image tool with S3 URI of  .png files to see if they are forged ones."
    "For stated facts, try your best to validate them by getting helps from the provided tool"
    "Store summary of documents and findings to a DynamoDB table insuranceclaim-reports-json in us-east-1, using claimId as a key"
    "State clearly, and point out which documents have suspicious points.",
    tools=[use_aws, detect_tampered_image, web_search, current_time],
)

@tool
def investigator(claim_id: str) -> str:
    """
    Investigates insurance claim documents for authenticity and fraud detection.
    Analyzes extracted data, checks document truthfulness, detects tampered images,
    and validates stated facts using web search and other tools.

    Args:
        claim_id (str): The claim ID to investigate

    Returns:
        str: Investigation findings and summary
    """
    response = investigator_agent(claim_id)
    return response.message["content"][0]["text"]


# investigator_agent(CLAIM_ID)


###################################

from strands_tools import use_aws, current_time, use_aws, python_repl, think
model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    boto_client_config=config,
)

adjustor_agent = Agent(
    name="adjustor",
    model=model,
    system_prompt="You are an claim adjustor. Find policy document for the insurance case, and find out the fair and accurate payout for the claim, and suggest adjusted payout."
    "Use input string as a claim_id."
    "You can find list of the documents by scanning a DynamoDB table `insuranceclaim-bda-results-raw` in us-east-1, using claimId as a key"
    "You can find summary and findings on the claim from a DynamoDB table `insuranceclaim-reports-json` in us-east-1, using claimId as a key"
    "Generate your suggestion for adjusting the claim case, and update `insuranceclaim-reports-json` with your suggestions.",
    tools=[use_aws],
)

@tool
def adjustor(claim_id: str) -> str:
    """
    Claims adjustor that analyzes policy documents and investigation findings
    to determine fair and accurate payout amounts for insurance claims.

    Args:
        claim_id (str): The claim ID to adjust

    Returns:
        str: Adjustment recommendations and payout suggestions
    """


    response = adjustor_agent(claim_id)
    return response.message["content"][0]["text"]


# Testing
# adjustor_agent(CLAIM_ID)

#########################

from strands_tools import think
from strands_tools import use_aws, current_time, use_aws
model = BedrockModel(
        model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        boto_client_config=config,
    )

report_agent = Agent(
    model=model,
    name="report",
    system_prompt="You are a insurnace claim agent.Combining the information, you generate a comprehensive report on the insurance claim."
    "Use input string as a claim_id."
    "The report should include summary of key information of the claim, claimant info and insights from the investigator and adjustor."
    "You can find list of the documents by scanning a DynamoDB table `insuranceclaim-bda-results-raw` in us-east-1, using claimId as a key"
    "Generate the final report in Markdown format."
    "Store the generated report to DynamoDB table insuranceclaim-reports-doc in us-east-1, using claimId as a key, `markdown` as an attribute",
    tools=[use_aws],
)

@tool
def report_generator(claim_id: str) -> str:
    """
    Generates comprehensive insurance claim reports in Markdown format.
    Combines information from document processing, investigation, and adjustment
    to create final claim reports.

    Args:
        claim_id (str): The claim ID to generate report for

    Returns:
        str: Generated report status and summary
    """
    

    response = report_agent(claim_id)
    return response.message["content"][0]["text"]


# Testing
# report_agent(CLAIM_ID)


#############################

from strands_tools import use_aws, current_time, use_aws, python_repl, think
model = BedrockModel(
        model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        boto_client_config=config,
    )

reviewer_agent = Agent(
    name="reviewer",
    model=model,
    system_prompt="You are a reviewer of insurance claim cases. "
    "Use input string as a claim_id."
    "A document is stored in DynamoDB table insuranceclaim-reports-doc in us-east-1. Retrieve `markdown` attribute using claimId as a key."
    "Review the documents and find out if anything is missing. If so, send it back.",
    tools=[use_aws, python_repl],
)

@tool
def reviewer(claim_id: str) -> str:
    """
    Reviews insurance claim reports for completeness and accuracy.
    Checks if any information is missing and provides feedback.

    Args:
        claim_id (str): The claim ID to review

    Returns:
        str: Review findings and recommendations
    """
    

    response = reviewer_agent(claim_id)
    return response.message["content"][0]["text"]



# Testing
# reviewer_agent(CLAIM_ID)

# Create main orchestrator agent that uses all the tools
model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0", boto_client_config=config
)

main_agent = Agent(
    name="insurance_claims_orchestrator",
    model=model,
    system_prompt="""You are an insurance claims processing orchestrator. 
    Use input string as a claim_id.
    You coordinate the entire claim processing workflow using specialized tools.
    
    For each claim, follow this workflow:
    1. Use document_processor to extract data from claim documents
    2. Use investigator to analyze documents for fraud and authenticity
    3. Use adjustor to determine fair payout amounts
    4. Use report_generator to create comprehensive reports
    5. Use reviewer to ensure report completeness
    
    Always process claims in this sequential order and provide status updates.""",
    tools=[
        document_processor,
        investigator,
        adjustor,
        report_generator,
        reviewer,
        detect_tampered_image,
        web_search,
        use_aws,
        current_time,
        python_repl,
    ],
)

# main_agent(CLAIM_ID)
# graph(CLAIM_ID)
#############
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload):
    """Process user input and return a response"""
    claim_id = payload["claimId"]

    # Use the main orchestrator agent to process the claim
    response = main_agent(claim_id)

    return {"result": response.message["content"][0]["text"]}


if __name__ == "__main__":
    app.run()

#!/usr/bin/env python3
"""
Test script to invoke the Agent Core runtime for insurance claim processing.
"""

import boto3
import json
import time
from datetime import datetime

# Configuration from .bedrock_agentcore.yaml
AGENT_ID = "insurance_claims_automation-HOyY6rBTuz"
AGENT_ARN = "arn:aws:bedrock-agentcore:us-west-2:670934798598:runtime/insurance_claims_automation-HOyY6rBTuz"
REGION = "us-west-2"
ACCOUNT_ID = "670934798598"

# Test claim ID
TEST_CLAIM_ID = "dev-use-case-02"


def invoke_agent_core_runtime(claim_id: str, session_id: str = None):
    """
    Invoke the Agent Core runtime to process an insurance claim.

    Args:
        claim_id (str): The claim ID to process
        session_id (str): Optional session ID for conversation continuity

    Returns:
        dict: Response from the agent
    """

    # Create Bedrock Agent Core client
    client = boto3.client("bedrock-agentcore", region_name=REGION)

    if not session_id:
        session_id = f"session-{int(time.time())}"

    payload = {"claimId": claim_id}

    try:
        print(f"🚀 Invoking Agent Core runtime for claim: {claim_id}")
        print(f"📋 Agent ID: {AGENT_ID}")
        print(f"🔗 Session ID: {session_id}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        print("-" * 50)

        response = client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_ARN,
            payload=json.dumps({
                "claimId":TEST_CLAIM_ID
                }
            )
        )

        print("✅ Agent Core invocation successful!")
        print(f"📄 Response: {json.dumps(response, indent=2, default=str)}")

        return response

    except Exception as e:
        print(f"❌ Error invoking Agent Core: {str(e)}")
        return None


def check_agent_status():
    """
    Check the status of the Agent Core runtime.
    """

    client = boto3.client("bedrock-agentcore", region_name=REGION)

    try:
        print("🔍 Checking Agent Core status...")

        # Try to get agent information
        response = client.get_agent(agentId=AGENT_ID)

        print("✅ Agent Core is accessible!")
        print(f"📋 Agent Details: {json.dumps(response, indent=2, default=str)}")

        return True

    except Exception as e:
        print(f"❌ Error checking agent status: {str(e)}")
        return False


def main():
    """
    Main function to test Agent Core invocation methods.
    """

    print("🏥 Insurance Claim Agent Core Runtime Test")
    print("=" * 60)

    # Check agent status first
    if not check_agent_status():
        print("⚠️  Agent Core might not be accessible. Continuing with tests...")

    print("\n" + "=" * 60)

    # Test 1: Standard runtime invocation
    print("🧪 Test 1: Standard Agent Core Runtime Invocation")
    result1 = invoke_agent_core_runtime(TEST_CLAIM_ID)

    print("\n" + "=" * 60)

    if result1:
        print("✅ Agent Core invocation worked!")
    else:
        print("❌ Agent Core invocation failed. Check your deployment.")


if __name__ == "__main__":
    main()

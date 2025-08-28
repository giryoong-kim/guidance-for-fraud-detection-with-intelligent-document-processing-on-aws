#!/usr/bin/env python3
"""
Simple test script to invoke Agent Core runtime.
"""

import boto3
import json

# Configuration
AGENT_ID = "insurance_claim_agent-VYi75NEJUs"
REGION = "us-east-1"
CLAIM_ID = "dev-use-case-01"

def simple_invoke():
    """Simple Agent Core invocation."""
    
    client = boto3.client('bedrock-agentcore', region_name=REGION)
    
    payload = {"claimId": CLAIM_ID}
    session_id = "test-session-001"
    
    try:
        print(f"Invoking Agent Core for claim: {CLAIM_ID}")
        
        response = client.invoke_runtime(
            agentId=AGENT_ID,
            sessionId=session_id,
            inputText=json.dumps(payload)
        )
        
        print("Success!")
        print(json.dumps(response, indent=2, default=str))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simple_invoke()
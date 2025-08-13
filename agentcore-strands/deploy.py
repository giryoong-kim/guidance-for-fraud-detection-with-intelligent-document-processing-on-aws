import boto3
import json
from bedrock_agentcore_starter_toolkit import Runtime

# Get session region and account id
session = boto3.Session()
        
# Get account ID
sts = session.client('sts')
identity = sts.get_caller_identity()
account_id = identity['Account']
region = "us-west-2"

# Get region
region = session.region_name

def create_agentcore_role():
    iam = boto3.client('iam')
    account_id = boto3.client("sts").get_caller_identity()["Account"]
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }
    
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {"Effect": "Allow", "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"], "Resource": "arn:aws:bedrock:*::foundation-model/*"},
            {"Effect": "Allow", "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"], "Resource": f"arn:aws:bedrock:*:{account_id}:inference-profile/*"},
            {"Effect": "Allow", "Action": ["bedrock:Retrieve", "bedrock:RetrieveAndGenerate"], "Resource": f"arn:aws:bedrock:{region}:{account_id}:knowledge-base/*"},
            {"Effect": "Allow", "Action": ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"], "Resource": f"arn:aws:ecr:{region}:{account_id}:repository/*"},
            {"Effect": "Allow", "Action": ["ecr:GetAuthorizationToken"], "Resource": "*"},
            {"Effect": "Allow", "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"], "Resource": f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/runtimes/*"},
            {"Effect": "Allow", "Action": ["cloudwatch:PutMetricData"], "Resource": "*"},
            {"Effect": "Allow", "Action": ["xray:PutTraceSegments", "xray:PutTelemetryRecords"], "Resource": "*"},
            {"Effect": "Allow", "Action": ["bedrock-agentcore:GetWorkloadAccessToken", "bedrock-agentcore:GetWorkloadAccessTokenForJWT", "bedrock-agentcore:GetWorkloadAccessTokenForUserId"], 
             "Resource": [f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default", 
                          f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default/workload-identity/*"]}
        ]
    }
    
    try:
        iam.create_role(RoleName="AgentCoreRuntimeRole-insurance-claims-automation", AssumeRolePolicyDocument=json.dumps(trust_policy))
        iam.put_role_policy(RoleName="AgentCoreRuntimeRole-insurance-claims-automation", PolicyName="Policy", PolicyDocument=json.dumps(policy))
    except: pass
    
    return f"arn:aws:iam::{account_id}:role/AgentCoreRuntimeRole-insurance-claims-automation"

if __name__=="__main__":
    agentcore_role_arn = create_agentcore_role()
   
    runtime=Runtime()

    runtime.configure(
        entrypoint="main.py",  # Python file containing agent implementation
        agent_name="insurance_claims_automation",  # Unique identifier for the deployed agent
        execution_role=agentcore_role_arn,  # IAM role for agent execution permissions
        auto_create_ecr=True,  # Automatic container registry management
        requirements_file="requirements.txt"  # Python dependencies specification
    )

    research_agent = runtime.launch(
        auto_update_on_conflict=True,
        env_vars={})

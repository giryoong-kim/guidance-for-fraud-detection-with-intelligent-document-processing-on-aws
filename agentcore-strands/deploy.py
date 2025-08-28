import boto3
import json
from bedrock_agentcore_starter_toolkit import Runtime

# Get session region and account id
session = boto3.Session()

# Get account ID
sts = session.client("sts")
identity = sts.get_caller_identity()
account_id = identity["Account"]
region = "us-east-1"

# Get region
#region = session.region_name


def create_agentcore_role():
    iam = boto3.client("iam")
    account_id = boto3.client("sts").get_caller_identity()["Account"]

    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            # Bedrock Model Invocation - All models and inference profiles
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock:Converse",
                    "bedrock:ConverseStream",
                ],
                "Resource": [
                    "arn:aws:bedrock:*::foundation-model/*",
                    f"arn:aws:bedrock:*:{account_id}:inference-profile/*",
                ],
            },
            # Bedrock Knowledge Base
            {
                "Effect": "Allow",
                "Action": ["bedrock:Retrieve", "bedrock:RetrieveAndGenerate"],
                "Resource": f"arn:aws:bedrock:{region}:{account_id}:knowledge-base/*",
            },
            # S3 - Full access to all buckets in the account
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket",
                    "s3:GetBucketLocation",
                    "s3:GetObjectVersion",
                    "s3:PutObjectAcl",
                    "s3:GetObjectAcl",
                ],
                "Resource": [f"arn:aws:s3:::*", f"arn:aws:s3:::*/*"],
            },
            # DynamoDB - Full access to all tables in the account
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                    "dynamodb:BatchGetItem",
                    "dynamodb:BatchWriteItem",
                    "dynamodb:DescribeTable",
                    "dynamodb:ListTables",
                ],
                "Resource": [
                    f"arn:aws:dynamodb:{region}:{account_id}:table/*",
                    f"arn:aws:dynamodb:{region}:{account_id}:table/*/index/*",
                ],
            },
            # Step Functions - Comprehensive access for BDA workflow execution
            {
                "Effect": "Allow",
                "Action": [
                    "states:StartExecution",
                    "states:DescribeExecution",
                    "states:StopExecution",
                    "states:ListExecutions",
                    "states:DescribeStateMachine",
                    "states:ListStateMachines",
                    "states:GetExecutionHistory",
                    "states:DescribeActivity",
                    "states:ListActivities"
                ],
                "Resource": [
                    f"arn:aws:states:{region}:{account_id}:stateMachine:*",
                    f"arn:aws:states:{region}:{account_id}:execution:*:*",
                    f"arn:aws:states:{region}:{account_id}:activity:*"
                ],
            },
            # SageMaker - For ML model invocation
            {
                "Effect": "Allow",
                "Action": ["sagemaker:InvokeEndpoint", "sagemaker:DescribeEndpoint"],
                "Resource": f"arn:aws:sagemaker:{region}:{account_id}:endpoint/*",
            },
            # ECR - For container management
            {
                "Effect": "Allow",
                "Action": ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"],
                "Resource": f"arn:aws:ecr:{region}:{account_id}:repository/*",
            },
            {
                "Effect": "Allow",
                "Action": ["ecr:GetAuthorizationToken"],
                "Resource": "*",
            },
            # CloudWatch Logs
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                "Resource": f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/runtimes/*",
            },
            # CloudWatch Metrics
            {
                "Effect": "Allow",
                "Action": ["cloudwatch:PutMetricData"],
                "Resource": "*",
            },
            # X-Ray Tracing
            {
                "Effect": "Allow",
                "Action": ["xray:PutTraceSegments", "xray:PutTelemetryRecords"],
                "Resource": "*",
            },
            # Bedrock AgentCore Workload Identity
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock-agentcore:GetWorkloadAccessToken",
                    "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
                    "bedrock-agentcore:GetWorkloadAccessTokenForUserId",
                ],
                "Resource": [
                    f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default",
                    f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default/workload-identity/*",
                ],
            },
        ],
    }

    role_name = "AgentCoreRuntimeRole-insurance-claims-automation"
    policy_name = "AgentCorePolicy"
    
    try:
        # Check if role exists and delete it if it does
        try:
            iam.get_role(RoleName=role_name)
            print(f"🔄 Role {role_name} already exists. Recreating...")
            
            # Delete attached policies first
            try:
                iam.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
                print(f"✅ Deleted existing policy {policy_name}")
            except iam.exceptions.NoSuchEntityException:
                pass
            
            # Delete the role
            iam.delete_role(RoleName=role_name)
            print(f"✅ Deleted existing role {role_name}")
            
        except iam.exceptions.NoSuchEntityException:
            print(f"🆕 Creating new role {role_name}")
        
        # Create the role
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for Bedrock AgentCore insurance claims automation with comprehensive AWS service access"
        )
        print(f"✅ Created role {role_name}")
        
        # Attach the policy
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy),
        )
        print(f"✅ Attached policy {policy_name} to role {role_name}")
        
    except Exception as e:
        print(f"❌ Error creating role: {str(e)}")
        raise

    return f"arn:aws:iam::{account_id}:role/{role_name}"


if __name__ == "__main__":
    agentcore_role_arn="arn:aws:iam::186297945978:role/AgentCoreRuntimeRole-insurance-claims-automation"
    #agentcore_role_arn = create_agentcore_role()

    runtime = Runtime()

    runtime.configure(
        entrypoint="main.py",  # Python file containing agent implementation
        agent_name="insurance_claims_automation_ue1",  # Unique identifier for the deployed agent
        execution_role=agentcore_role_arn,  # IAM role for agent execution permissions
        auto_create_ecr=True,  # Automatic container registry management
        requirements_file="requirements.txt",  # Python dependencies specification
    )

    research_agent = runtime.launch(auto_update_on_conflict=True, env_vars={
        "AWS_DEFAULT_REGION": region,
        "AWS_ACCOUNT_ID": account_id
    })

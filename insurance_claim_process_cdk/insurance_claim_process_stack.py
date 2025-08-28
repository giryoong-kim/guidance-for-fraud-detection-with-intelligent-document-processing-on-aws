import configparser
from aws_cdk import (
    # Duration,
    Stack,
    NestedStack,
    # aws_sqs as sqs,
)
from constructs import Construct

from insurance_claim_process_cdk.api import ApiStack
from insurance_claim_process_cdk.dynamodb import DynamoDBStack
from insurance_claim_process_cdk.frontend import FrontEndStack
from insurance_claim_process_cdk.lambdafn import LambdaStack
from insurance_claim_process_cdk.s3 import S3Stack
from insurance_claim_process_cdk.sns import NotificationStack
from insurance_claim_process_cdk.statemachines import BaseSfnStateMachineStack
from insurance_claim_process_cdk.workflow import WorkflowStack

config = configparser.ConfigParser()
config.read('config.ini')

class InsuranceClaimProcessStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.template_options.description = "Guidance for Fraud Detection with Intelligent Document Processing on AWS(SO9033)"

        workflow = Stack(self, "InsuranceClaimProcessWorkflow")
        stepfunctions = BaseSfnStateMachineStack(workflow, "InsuranceClaimProcessStepFunctions", config["BDA"]["projectArn"])
        s3 = S3Stack(workflow, "InsuranceClaimProcessS3")
        dynamodb = DynamoDBStack(workflow, "InsuranceClaimProcessDynamoDB")
        lambda_ = LambdaStack(workflow, "InsuranceClaimProcessLambda")
        sns = NotificationStack(workflow, "InsuranceClaimProcessSNS")

        frontend = FrontEndStack(self, "InsuranceClaimProcessFrontEnd")
        # Pass the lambda stack to the API stack so it can reference the proxy functions
        api = ApiStack(self, "InsuranceClaimProcessApi", lambda_stack=lambda_)

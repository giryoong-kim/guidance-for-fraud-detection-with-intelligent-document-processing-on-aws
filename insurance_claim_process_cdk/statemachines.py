import os
import json
from glob import glob

from aws_cdk import (
    # Duration,
    NestedStack,
    aws_stepfunctions as stepfunctions,
    aws_iam as iam,
    aws_logs as logs,
    RemovalPolicy
)
from constructs import Construct


class BaseSfnStateMachineStack(NestedStack):
    definitions_dir = os.path.join(os.path.dirname(__file__), "stepfunctions", "definitions")
    policies_dir = os.path.join(os.path.dirname(__file__), "stepfunctions", "policies")

    def __init__(
        self, scope: Construct, construct_id: str, bda_project_arn, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        for json_file in os.listdir(self.definitions_dir):
            if not os.path.isdir(json_file):
                file_name = json_file.split(".")[0]
                step_policy_file = os.path.join(self.policies_dir, json_file)
 
                with open(step_policy_file) as f:
                    policy = json.loads(f.read().replace("<AWS_REGION>", self.region).replace(
                        "<AWS_ACCOUNT>", self.account).replace("<BDA_PROJECT_ARN>",bda_project_arn))

                policy_document = iam.PolicyDocument.from_json(policy)
                role = iam.Role(
                    self,
                    f"{file_name}-sfn-role",
                    role_name=f"{file_name}-{self.region}-sfn-role",
                    assumed_by=iam.ServicePrincipal("states.amazonaws.com"),
                    inline_policies=({"policy_doc": policy_document}),
                )

                statemachine_def_file = os.path.join(self.definitions_dir, json_file)

                with open(statemachine_def_file) as f:
                    definition = f.read().replace("<AWS_REGION>", self.region).replace(
                        "<AWS_ACCOUNT>", self.account).replace("<BDA_PROJECT_ARN>",bda_project_arn)

                log_group = logs.LogGroup(
                    self,
                    f"StepFunctionsLogGroup-{file_name}",
                    log_group_name=f"/aws/vendedlogs/states/insurance-claim-{file_name}",
                    retention=logs.RetentionDays.ONE_WEEK,  # Adjust retention as needed
                    removal_policy=RemovalPolicy.DESTROY
)

                logging_configuration_property = stepfunctions.CfnStateMachine.LoggingConfigurationProperty(
                    destinations=[stepfunctions.CfnStateMachine.LogDestinationProperty(
                        cloud_watch_logs_log_group=stepfunctions.CfnStateMachine.CloudWatchLogsLogGroupProperty(
                            log_group_arn=log_group.log_group_arn
                        )
                    )],
                    include_execution_data=False,
                    level="ALL"
                )

                cfn_state_machine = stepfunctions.CfnStateMachine(
                    self,
                    f"{file_name}",
                    role_arn=role.role_arn,
                    state_machine_name=f"{file_name}",
                    definition_string=definition,
                    tracing_configuration = stepfunctions.CfnStateMachine.TracingConfigurationProperty(
                        enabled=True
                    ),
                    logging_configuration=logging_configuration_property
                    #state_machine_type="EXPRESS"
                )

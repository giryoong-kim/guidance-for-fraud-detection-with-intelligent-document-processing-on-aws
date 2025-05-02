import os

from aws_cdk import (
    # Duration,
    NestedStack,
    aws_dynamodb,
    RemovalPolicy)
from constructs import Construct


class DynamoDBStack(NestedStack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # create dynamo table
        result_raw = aws_dynamodb.Table(
            self, "insuranceclaim-bda-results-raw",
            table_name="insuranceclaim-bda-results-raw",
            partition_key=aws_dynamodb.Attribute(
                name="claimId",
                type=aws_dynamodb.AttributeType.STRING
            ),
            sort_key=aws_dynamodb.Attribute(name="name", type=aws_dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        reports_doc = aws_dynamodb.Table(
            self, "insuranceclaim-reports-doc",
            table_name="insuranceclaim-reports-doc",
            partition_key=aws_dynamodb.Attribute(
                name="claimId",
                type=aws_dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        reports_json = aws_dynamodb.Table(
            self, "insuranceclaim-reports-json",
            table_name="insuranceclaim-reports-json",
            partition_key=aws_dynamodb.Attribute(
                name="claimId",
                type=aws_dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY
        )
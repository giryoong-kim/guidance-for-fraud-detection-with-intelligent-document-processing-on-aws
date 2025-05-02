import os

from aws_cdk import (
    # Duration,
    NestedStack,
    Fn,
    aws_s3,
    aws_iam,
    aws_kms,
    RemovalPolicy,
)
from constructs import Construct

class S3Stack(NestedStack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        input_bucket = aws_s3.Bucket(
            self,
            f"insuranceclaim-input-bucket",
            bucket_name=f"insuranceclaim-input-{self.account}-{self.region}",
            encryption=aws_s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            enforce_ssl=True,
            #auto_delete_objects=True,
            object_ownership=aws_s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
        )

        input_bucket.add_cors_rule(
            allowed_methods=[aws_s3.HttpMethods.PUT],
            allowed_origins=["*"],
            allowed_headers=["*"],
            max_age=3000
        )

        output_bucket = aws_s3.Bucket(
            self,
            f"insuranceclaim-output-bucket",
            bucket_name=f"insuranceclaim-output-{self.account}-{self.region}",
            encryption=aws_s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            enforce_ssl=True,
            #auto_delete_objects=True,
            object_ownership=aws_s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
        )


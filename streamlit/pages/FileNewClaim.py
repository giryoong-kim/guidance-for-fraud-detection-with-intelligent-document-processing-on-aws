"""
Streamlit page
"""

import streamlit as st
import boto3
import json
import os

account_number = boto3.client('sts').get_caller_identity().get('Account')
region_name = os.environ.get("AWS_REGION", "us-west-2")
bda_project_id = "6a332905df3a" # TODO

# Streamlit form consist of Claim ID, file upload control
st.title("File a new claim")

st.markdown("## Claim ID")
claim_id = st.text_input("Enter Claim ID")


st.markdown("## File Upload")

files = st.file_uploader("Upload files", type=["pdf", "png", "m4a"], accept_multiple_files=True)
if files is not None:
    if not claim_id:
        st.error("Please enter a claim ID")
        st.stop()


    # A button to start upload
    if st.button("Upload"):
        st.write("Uploading files...")
        s3 = boto3.client("s3", region_name=region_name)
        
        # Upload the file to S3
        for file in files:
            s3.upload_fileobj(
                file,
                f'insuranceclaim-input-{account_number}-{region_name}',
                os.path.join(claim_id, file.name),
            )
        # Display a success message
        st.success("File uploaded successfully!")

        # Invoke Step Function
        client = boto3.client("stepfunctions", region_name=region_name)
        response = client.start_execution(
            stateMachineArn=f"arn:aws:states:{region_name}:{account_number}:stateMachine:insuranceclaim-Main_Workflow",
            input=json.dumps(
                {
                    "claimId": claim_id,
                    "inputBucket": f"insuranceclaim-input-{account_number}-{region_name}",
                    "outputBucket": f"insuranceclaim-output-{account_number}-{region_name}",
                    "bdaProjectArn": f"arn:aws:bedrock:{region_name}:{account_number}:data-automation-project/{bda_project_id}",
                }
            ),
        )
        st.success("Starting Document Processing.")

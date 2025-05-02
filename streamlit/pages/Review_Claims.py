'''
Streamlit page
'''
import streamlit as st
import boto3
import json
import os

# Read claimId attribute from DynamoDB table insuranceclaim-reports-html
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get("AWS_REGION", "us-west-2"))


table = dynamodb.Table('insuranceclaim-reports-doc')
response = table.scan(Limit=100, ProjectionExpression='claimId')
items = response['Items']

# Get a list of claim IDs
claim_ids = [item['claimId'] for item in items]
st.sidebar.markdown("## Claim IDs")
claim_id = st.sidebar.selectbox("Select a claim ID", claim_ids)

# Add two taps: one for the document format and one for JSON form
tab1, tab2, tab3 = st.tabs(["Claim Report", "JSON", "Raw"])

with tab1:
    if claim_id:
        # Get the claim report from DynamoDB table insuranceclaim-reports-doc
        table = dynamodb.Table('insuranceclaim-reports-doc')
        response = table.get_item(Key={'claimId': claim_id})
        item = response['Item']
        # Display the claim report
        st.html(item['doc'])

with tab2:
    if claim_id:
        # Get the claim report from DynamoDB table insuranceclaim-reports-json
        table = dynamodb.Table('insuranceclaim-reports-json')
        response = table.get_item(Key={'claimId': claim_id})
        item = response['Item']
        # Display the claim report
        st.markdown("## Claim Report")
        st.json(item)
with tab3:
    if claim_id:
        # Get the claim report from DynamoDB table insuranceclaim-bda-results-raw
        table = dynamodb.Table('insuranceclaim-bda-results-raw')
        response = table.query(
            KeyConditionExpression='claimId = :claimId',
            ExpressionAttributeValues={
                ':claimId': claim_id
            }
        )
        items = response['Items']
        # Display the claim report
        st.markdown("## Claim documents")
        st.json(items)

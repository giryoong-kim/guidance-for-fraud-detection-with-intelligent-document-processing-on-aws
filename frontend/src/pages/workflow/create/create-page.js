import * as React from "react";
import {
  Flashbar,
  BreadcrumbGroup,
  Button,
  Input,
  ContentLayout,
  FileUpload,
  Form,
  FormField,
  Header,
  SpaceBetween,
} from "@cloudscape-design/components";
//import { useOnFollow } from "../common/hooks/use-on-follow";
import { API_ENDPOINT, APP_NAME } from "../../../common/constants";
import BaseAppLayout from "../../../components/base-app-layout";
import uploadFiles from "../../../components/upload-files";
import { Amplify, Auth } from "aws-amplify";


function validateClaimId(claimId) {
  if (claimId.length < 5) {
    return "Claim ID must be at least 5 characters long";
  }
  if (claimId.length > 20) {
    return "Claim ID must be less than 20 characters long";
  }
  if (!/^[a-zA-Z0-9-]+$/.test(claimId)) {
    return "Claim ID must only contain letters, numbers and dashes";
  }
  return undefined;
}

function validateFiles(files) {
  if (files.length == 0) {
    return "Please upload at least one file";
  }
  return undefined;
}

export default function Create({ token }) {
  const [files, setFiles] = React.useState([]);
  const [claimId, setClaimId] = React.useState("");
  const [submitted, setSubmitted] = React.useState(false);
  const [succesfulSubmission, setSuccesfulSubmission] = React.useState(false);

  return (
    <BaseAppLayout
      notifications={
        succesfulSubmission && (
          <Flashbar
            items={[
              {
                type: "success",
                dismissible: true,
                content:
                  "Claim ID " + claimId + " has been submitted for processing.",
                id: "success",
              },
            ]}
          />
        )
      }
      breadcrumbs={
        <BreadcrumbGroup
          //onFollow={onFollow}
          items={[
            {
              text: APP_NAME,
              href: "/",
            },
            {
              text: "Create a new claim",
              href: "/workflow/create",
            },
          ]}
          expandAriaLabel="Show path"
          ariaLabel="Breadcrumbs"
        />
      }
      content={
        <ContentLayout
          header={<Header variant="h1">Create a new claim</Header>}
        >
          <Form
            actions={
              <SpaceBetween direction="horizontal" size="xs">
                <Button
                  formAction="none"
                  variant="link"
                  onClick={() => {
                    setSubmitted(false);
                    setClaimId("");
                    setFiles([]);
                    setSuccesfulSubmission(false);
                  }}
                >
                  Cancel
                </Button>
                <Button
                  formAction="Submit"
                  variant="primary"
                  onClick={() => {
                    setSubmitted(true);
                    if (validateClaimId(claimId) || validateFiles(files)) {
                      return;
                    }
                    uploadFiles(files, claimId, token);
                    // Invoke API to start SFN to process documents
                    const startProcessing = async () => {
                      try {
                        const response = await fetch(
                          API_ENDPOINT+"/start-claim-processing?claim_id=" +
                            claimId,
                          {
                            method: "GET",
                            headers: {
                              'Authorization': token.token,
                              'Content-Type': 'application/json',
                            },
                          }
                        );
                        
                        if (!response.ok) {
                          throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        
                        const data = await response.json();
                        console.log('Processing started:', data);
                        setSuccesfulSubmission(true);
                      } catch (error) {
                        console.error('Error starting claim processing:', error);
                        // You might want to show an error message to the user here
                      }
                    };
                    
                    startProcessing();
                  }}
                >
                  Submit
                </Button>
              </SpaceBetween>
            }
            header={
              <Header variant="h3">
                File a new claim with supporting documents
              </Header>
            }
          >
            <SpaceBetween size="l">
              <FormField
                label="New Claim ID"
                errorText={submitted && validateClaimId(claimId)}
              >
                <Input
                  value={claimId}
                  onChange={(event) => setClaimId(event.detail.value)}
                />
              </FormField>
              <br />
              <FormField
                label="Upload files"
                description="Create a new claim case with documents and media files."
                errorText={submitted && validateFiles(files)}
              >
                <FileUpload
                  onChange={({ detail }) => setFiles(detail.value)}
                  value={files}
                  i18nStrings={{
                    uploadButtonText: (e) =>
                      e ? "Choose files" : "Choose file",
                    dropzoneText: (e) =>
                      e ? "Drop files to upload" : "Drop file to upload",
                    removeFileAriaLabel: (e) => `Remove file ${e + 1}`,
                    limitShowFewer: "Show fewer files",
                    limitShowMore: "Show more files",
                    errorIconAriaLabel: "Error",
                    warningIconAriaLabel: "Warning",
                  }}
                  multiple
                  showFileLastModified
                  showFileSize
                  showFileThumbnail
                  tokenLimit={10}
                  constraintText="PDFs, images or audio files"
                />
              </FormField>
            </SpaceBetween>
          </Form>
        </ContentLayout>
      }
    />
  );
}

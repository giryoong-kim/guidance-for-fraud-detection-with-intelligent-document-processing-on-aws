import React, { useState } from "react";
import { API_ENDPOINT } from "../../../common/constants";
import { useParams } from "react-router";
import ClaimReport from "../../../components/claim-report";

import {
  Alert,
  BreadcrumbGroup,
  Container,
  Link,
  Box,
  Button,
  TextFilter,
  Pagination,
  CollectionPreferences,
  ContentLayout,
  Header,
  Table,
  SpaceBetween,
} from "@cloudscape-design/components";
//import { useOnFollow } from "../common/hooks/use-on-follow";
import { APP_NAME } from "../../../common/constants";
import BaseAppLayout from "../../../components/base-app-layout";

const getClaimReport = async (claimId, token) => {
  try {
    const headers = {
      'Authorization': token.token,
      'Content-Type': 'application/json',
    };
    
    const response = await fetch(
      API_ENDPOINT+"/get-claim-report?claimId=" + claimId,
      {
        method: "GET",
        headers: headers,
      }
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    //console.log(data.markdown)
    return data.markdown;
  } catch (error) {
    console.error('Error fetching claim report:', error);
    throw error;
  }
};

export default function ReviewDetail({ token }) {
  //const onFollow = useOnFollow();
  const [claimReport, setClaimReport] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  let params = useParams();
  console.log(params);

  const reload = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getClaimReport(params.claimId, token);
      setClaimReport(data);
    } catch (err) {
      setError(err.message);
      console.error('Failed to load claim report:', err);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    if (token && params.claimId) {
      reload();
    }
  }, [token, params.claimId]);

  return (
    <BaseAppLayout
      breadcrumbs={
        <BreadcrumbGroup
          //onFollow={onFollow}
          items={[
            {
              text: APP_NAME,
              href: "/",
            },
            {
              text: "Review claims",
              href: "/workflow/review",
            },
            {
              text: params.claimId,
              href: "/workflow/review",
            },
          ]}
          expandAriaLabel="Show path"
          ariaLabel="Breadcrumbs"
        />
      }
      content={
        <ContentLayout header={<Header variant="h1">Claim Report</Header>}>
          <SpaceBetween size="l">
            {error && (
              <Alert
                statusIconAriaLabel="Error"
                type="error"
                header="Failed to load claim report"
                action={
                  <Button onClick={reload}>
                    Retry
                  </Button>
                }
              >
                {error}
              </Alert>
            )}
            {loading ? (
              <div>Loading claim report...</div>
            ) : (
              <ClaimReport claimData={claimReport} />
            )}
          </SpaceBetween>
        </ContentLayout>
      }
    />
  );
}

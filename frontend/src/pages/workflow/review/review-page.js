import React, { useState } from "react";
import { API_ENDPOINT } from "../../../common/constants";
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

// Script to invoke GET API for claims
const getClaims = async (token) => {
  try {
    console.log("Fetching claims with token:", token);
    const headers = {
      Authorization: token.token,
      "Content-Type": "application/json",
    };

    const response = await fetch(API_ENDPOINT + "/get-claims", {
      method: "GET",
      headers: headers,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching claims:", error);
    throw error;
  }
};

export default function Review({ token }) {
  //const onFollow = useOnFollow();
  const [claims, setClaims] = useState([]);
  const [selectedItems, setSelectedItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const reload = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getClaims(token);
      setClaims(data);
    } catch (err) {
      setError(err.message);
      console.error("Failed to load claims:", err);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    if (token) {
      reload();
    }
  }, [token]);

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
          ]}
          expandAriaLabel="Show path"
          ariaLabel="Breadcrumbs"
        />
      }
      content={
        <ContentLayout header={<Header variant="h1">Review claims</Header>}>
          <SpaceBetween size="l">
            {error && (
              <Alert
                statusIconAriaLabel="Error"
                type="error"
                header="Failed to load claims"
                action={<Button onClick={reload}>Retry</Button>}
              >
                {error}
              </Alert>
            )}
            <Table
              loading={loading}
              //loading = {reload()}
              renderAriaLive={({ firstIndex, lastIndex, totalItemsCount }) =>
                `Displaying items ${firstIndex} to ${lastIndex} of ${totalItemsCount}`
              }
              onSelectionChange={({ detail }) =>
                setSelectedItems(detail.selectedItems)
              }
              selectedItems={selectedItems}
              ariaLabels={{
                selectionGroupLabel: "Items selection",
                allItemsSelectionLabel: () => "select all",
                itemSelectionLabel: ({ selectedItems }, item) => item.name,
              }}
              columnDefinitions={[
                {
                  id: "claimId",
                  header: "Claim ID",
                  cell: (item) => (
                    <Link href={"/workflow/review/" + item.claimId}>
                      {item.claimId}
                    </Link>
                  ),
                  sortingField: "claimId",
                  isRowHeader: true,
                },
                {
                  id: "claimDate",
                  header: "Claim Date",
                  cell: (item) => item.dateFiled,
                  sortingField: "alt",
                },
                {
                  id: "incidentDate",
                  header: "Incident Date",
                  sortingField: "alt",
                  cell: (item) => item.incidentDate,
                },
                {
                  id: "description",
                  header: "Description",
                  cell: (item) => item.description,
                },
              ]}
              columnDisplay={[
                { id: "claimId", visible: true },
                { id: "claimFileDate", visible: true },
                { id: "incidentDate", visible: true },
                { id: "description", visible: true },
              ]}
              enableKeyboardNavigation
              items={claims}
              loadingText="Loading resources"
              selectionType="multi"
              trackBy="name"
              empty={
                <Box
                  margin={{ vertical: "xs" }}
                  textAlign="center"
                  color="inherit"
                >
                  <SpaceBetween size="m">
                    <b>No resources</b>
                    <Button>Create resource</Button>
                  </SpaceBetween>
                </Box>
              }
              /*filter={
                <TextFilter
                  filteringPlaceholder="Find resources"
                  filteringText=""
                  countText="0 matches"
                />
              }*/
              header={
                <Header counter={" (" + claims.length + ") "}>Claims</Header>
              }
              //pagination={<Pagination currentPageIndex={1} pagesCount={2} />}
              preferences={
                <CollectionPreferences
                  title="Preferences"
                  confirmLabel="Confirm"
                  cancelLabel="Cancel"
                  preferences={{
                    pageSize: 10,
                    contentDisplay: [
                      { id: "variable", visible: true },
                      { id: "value", visible: true },
                      { id: "type", visible: true },
                      { id: "description", visible: true },
                    ],
                  }}
                  pageSizePreference={{
                    title: "Page size",
                    options: [
                      { value: 10, label: "10 resources" },
                      { value: 20, label: "20 resources" },
                    ],
                  }}
                  wrapLinesPreference={{}}
                  stripedRowsPreference={{}}
                  contentDensityPreference={{}}
                  contentDisplayPreference={{
                    options: [
                      {
                        id: "variable",
                        label: "Variable name",
                        alwaysVisible: true,
                      },
                      { id: "value", label: "Text value" },
                      { id: "type", label: "Type" },
                      { id: "description", label: "Description" },
                    ],
                  }}
                  stickyColumnsPreference={{
                    firstColumns: {
                      title: "Stick first column(s)",
                      description:
                        "Keep the first column(s) visible while horizontally scrolling the table content.",
                      options: [
                        { label: "None", value: 0 },
                        { label: "First column", value: 1 },
                        { label: "First two columns", value: 2 },
                      ],
                    },
                    lastColumns: {
                      title: "Stick last column",
                      description:
                        "Keep the last column visible while horizontally scrolling the table content.",
                      options: [
                        { label: "None", value: 0 },
                        { label: "Last column", value: 1 },
                      ],
                    },
                  }}
                />
              }
            />
          </SpaceBetween>
        </ContentLayout>
      }
    />
  );
}

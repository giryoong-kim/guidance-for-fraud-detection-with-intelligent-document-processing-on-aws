import {
  Alert,
  Grid,
  Container,
  Link,
  Box,
  Button,
  TextFilter,
  Pagination,
  CollectionPreferences,
  KeyValuePairs,
  ContentLayout,
  Header,
  Table,
  SpaceBetween,
  TextContent,
} from "@cloudscape-design/components";

function BulletList({ items }) {
  return (
    <div>
      <ul>
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default function ClaimReport(props) {
  const claimData = props.claimData;
  console.log(claimData);
  if (claimData.length == 0) {
    return "Loading";
  }

  return (
    <div>
      <ContentLayout
        header={
          <SpaceBetween size="s">
            <Header
              variant="h1"
              description={
                " Policy No: " +
                claimData.policyNo +
                "\t|\tClaim Date: " +
                claimData.claimInfo.dateFiled
              }
            >
              ID: {claimData.claimId}
            </Header>
            {claimData.fraudWarning && (
              <Alert type="warning">{claimData.suspicion}</Alert>
            )}
          </SpaceBetween>
        }
      >
        <SpaceBetween size="l">
          <SpaceBetween size="s">
            <Container
              header={
                <Header
                  variant="h2"
                  description={claimData.incidentInfo.description}
                >
                  Claim Info
                </Header>
              }
            >
              <SpaceBetween size="s">
                <KeyValuePairs
                  columns={2}
                  items={[
                    {
                      label: "Claim date",
                      value: claimData.claimInfo.claimFiledDate,
                    },
                    {
                      label: "Incident date",
                      value: claimData.incidentInfo.date,
                    },
                    {
                      label: "Estimated Value of Damage",
                      value: claimData.claimInfo.estimatedValueOfDamage,
                    },
                    {
                      label: "Estimated Cost of Repair",
                      value: claimData.claimInfo.estimatedCostOfRepairs,
                    },
                    {
                      label: "Contact",
                      value: claimData.policyInfo.agentContact,
                    },
                    {
                      label: "Insurance Company",
                      value: claimData.policyInfo.insuranceCompany,
                    },
                  ]}
                />
              </SpaceBetween>
            </Container>
          </SpaceBetween>

          <Container header={<Header variant="h2">Claimed Property</Header>}>
            <SpaceBetween size="s">
              <KeyValuePairs
                columns={2}
                items={[
                  {
                    label: "Address",
                    value: claimData.propertyInfo.address,
                  },
                  {
                    label: "Type",
                    value: claimData.propertyInfo.typeOfProperty,
                  },
                ]}
              />
              <Box>{claimData.propertyInfo.additionalInfo}</Box>
              <Box variant="h4" padding={{ top: "m" }}>
                Description of Damage
              </Box>
              <TextContent>{claimData.descriptionOfDamage}</TextContent>
            </SpaceBetween>
          </Container>
          <Container
            header={
              <Header
                variant="h2"
                //description="Claim details"
              >
                Insurance Policy
              </Header>
            }
          >
            <SpaceBetween size="s">
              <KeyValuePairs
                columns={2}
                items={[
                  {
                    label: "Policy Holder Name",
                    value: claimData.policyHolderDetails.name,
                  },
                  {
                    label: "Policy Address",
                    value: claimData.policyHolderDetails.address,
                  },
                  {
                    label: "Policy No",
                    value: claimData.policyNo,
                  },
                  {
                    label: "Agent",
                    value: claimData.policyInfo.agentName,
                  },
                  {
                    label: "Contact",
                    value: claimData.policyInfo.agentContact,
                  },
                  {
                    label: "Insurance Company",
                    value: claimData.policyInfo.insuranceCompany,
                  },
                ]}
              />
            </SpaceBetween>
          </Container>

          <Container
            header={
              <Header
                variant="h2"
                //description="Claim details"
              >
                Proofs of Damage
              </Header>
            }
          >
            <SpaceBetween size="s">
              <Box variant="h4" padding={{ top: "m" }}>
                Customer Call Records
              </Box>
              <Box variant="p">{claimData.callRecordingsSummary}</Box>
              <Box variant="h4" padding={{ top: "m" }}>
                Submitted documents
              </Box>
              <Table
                renderAriaLive={({ firstIndex, lastIndex, totalItemsCount }) =>
                  `Displaying items ${firstIndex} to ${lastIndex} of ${totalItemsCount}`
                }
                items={claimData.proofOfDamage}
                columnDefinitions={[
                  {
                    id: "type",
                    header: "Type",
                    width: 100,
                    cell: (item) => item.type,
                  },
                  {
                    id: "description",
                    header: "Description",
                    width: 550,
                    cell: (item) => item.description,
                  },
                  {
                    id: "validity",
                    header: "Validity",
                    width: 120,
                    cell: (item) => item.validity,
                  },
                  {
                    id: "link",
                    header: "Link",
                    cell: (item) => (
                      <Link href={item.link} target="_blank">
                        {item.link}
                      </Link>
                    ),
                  },
                ]}
                columnDisplay={[
                  { id: "type", visible: true },
                  { id: "description", visible: true },
                  { id: "validity", visible: true },
                  { id: "link", visible: true },
                ]}
                resizableColumns
                wrapLines
              />
            </SpaceBetween>
            <Box variant="h4" padding={{ top: "m" }}>
              Witness
            </Box>
            <KeyValuePairs
              columns={2}
              items={[
                {
                  label: "Name",
                  value: claimData.witness.name,
                },
                {
                  label: "Contact",
                  value: claimData.witness.contactInformation,
                },
                {
                  label: "Relationship",
                  value: claimData.witness.relationshipToClaimant,
                },
              ]}
            />
          </Container>
          <Container
            header={
              <Header
                variant="h2"
                //description="Claim details"
              >
                Cost Estimation
              </Header>
            }
          >
            <Table
              renderAriaLive={({ firstIndex, lastIndex, totalItemsCount }) =>
                `Displaying items ${firstIndex} to ${lastIndex} of ${totalItemsCount}`
              }
              items={claimData.estimatesOfTotalCostToRepairPerEachVendor}
              columnDefinitions={[
                {
                  id: "vendor",
                  header: "Vendor Name",
                  width: 200,
                  cell: (item) => item.vendorName,
                },
                {
                  id: "scope",
                  header: "Scope of Work",
                  width: 250,
                  cell: (item) => item.scopeOfWork,
                },
                {
                  id: "cost",
                  header: "Cost",
                  width: 150,
                  cell: (item) => item.totalCost,
                },
              ]}
              columnDisplay={[
                { id: "vendor", visible: true },
                { id: "scope", visible: true },
                { id: "cost", visible: true },
              ]}
              resizableColumns
              wrapLines
            />
          </Container>
          <Container
            header={
              <Header
                variant="h2"
                //description="Claim details"
              >
                AI Generated Reviews
              </Header>
            }
          >
            <Box variant="h2" padding={{ top: "m" }}>
              Observations
            </Box>
            <TextContent>
              <p>{claimData.observations}</p>
            </TextContent>
            <Box variant="h2" padding={{ top: "m" }}>
              Insights
            </Box>
            <TextContent>
              <p>{claimData.insights}</p>
            </TextContent>
          </Container>
        </SpaceBetween>
      </ContentLayout>
    </div>
  );
}

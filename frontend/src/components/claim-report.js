import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
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

// Custom components to map markdown elements to CloudScape components
const MarkdownComponents = {
  h1: ({ children }) => <Header variant="h1">{children}</Header>,
  h2: ({ children }) => <Header variant="h2">{children}</Header>,
  h3: ({ children }) => <Header variant="h3">{children}</Header>,
  p: ({ children }) => (
    <TextContent>
      <p>{children}</p>
    </TextContent>
  ),
  ul: ({ children }) => (
    <TextContent>
      <ul>{children}</ul>
    </TextContent>
  ),
  ol: ({ children }) => (
    <TextContent>
      <ol>{children}</ol>
    </TextContent>
  ),
  li: ({ children }) => <li>{children}</li>,
  strong: ({ children }) => <strong>{children}</strong>,
  em: ({ children }) => <em>{children}</em>,
  code: ({ children }) => <Box variant="code">{children}</Box>,
  pre: ({ children }) => <Box variant="pre">{children}</Box>,
  blockquote: ({ children }) => (
    <Box
      margin={{ left: "m" }}
      padding={{ left: "s" }}
      color="text-status-info"
    >
      {children}
    </Box>
  ),
  a: ({ href, children }) => (
    <Link href={href} external>
      {children}
    </Link>
  ),
};

export default function ClaimReport(props) {
  const claimData = props.claimData;
  console.log(claimData);

  if (!claimData || claimData.length === 0) {
    return <TextContent>Loading...</TextContent>;
  }

  // Check if claimData is a string (markdown) or already processed data
  const isMarkdown = typeof claimData === "string";

  return (
    <div>
      <ContentLayout>
        <SpaceBetween size="l">
          {isMarkdown ? (
            <ReactMarkdown
              components={MarkdownComponents}
              remarkPlugins={[remarkGfm]}
            >
              {claimData}
            </ReactMarkdown>
          ) : (
            <TextContent>{claimData}</TextContent>
          )}
        </SpaceBetween>
      </ContentLayout>
    </div>
  );
}

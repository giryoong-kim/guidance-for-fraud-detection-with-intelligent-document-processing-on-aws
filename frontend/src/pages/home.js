import { TextContent } from "@cloudscape-design/components";
import BaseAppLayout from "../components/base-app-layout";

export default function HomePage() {
  return (
    <BaseAppLayout
      content={
        <TextContent>
          <h1>Description</h1>
          <br/>
          <h2>Automated Claims Processing using Amazon Bedrock</h2>
          <p>Financial institutions face multifaceted challenges in modern claims processing, primarily stemming from the overwhelming 
          influx of unstructured data (documents, images, videos, and audio recordings) that lacks predefined schema and standardized 
          processing frameworks.</p>
          <p>This solution focuses on automating multi-modal documents processing in insurance clasims. It extracts data from document forms, images and audio files and flow them through machine learning models and GenAI to derive insights to produce reports in both of human and machine readable formats.</p>
          <br/><br/>
          <h2>Solution Overview</h2>
          <p>This solution consists of following key components:</p>
          <ul><li>
          Amazon Bedrock Data Automation (BDA): A GenAI-powered capability of Bedrock that streamlines the extraction of valuable insights from unstructured, multimodal content like documents, images, audio, and videos. It is used for extract text from forms, extracting describtion of images and transcringing/summarizing audio clips from customer calls.
          Amazon SageMaker AI: A cloud-based machine learning(ML) platform that helps users build, train, and deploy ML models. The solution trains and deploys a document tampering detection model to SageMaker Endpoint for fraud-detection.
          Amazon S3, AWS Lambda, AWS Step Functions and Amazon DynamoDB: These AWS serverless services combines AI/ML functionalies into a seamless workflows.<br/>
          </li></ul>
          <br/>
          <img src = "/images/reference-architecture.png"/>
        </TextContent>
      }
    />
  );
}
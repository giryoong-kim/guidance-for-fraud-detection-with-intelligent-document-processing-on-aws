// Javascript to upload files from local to S3 bucket using presigned URLs

import { API_ENDPOINT } from "../common/constants";


function uploadFile(file, signedUrl) {
  console.log("Uploading file to S3", file);
  return fetch(signedUrl.uploadURL, {
    method: "PUT",
    headers: {
      "Content-Type": "application/octet-stream",
    },
    body: file,
  });
}

function getSignedUrl(file, claimId, token) {
  const headers = {
    Authorization: token.token,
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": "true",
  };
  console.log("Getting signed URL for file", file);
  console.debug("Token", token.token);
  return fetch(
    API_ENDPOINT +
      "/get-presigned-post-url?file=" +
      file +
      "&claim_id=" +
      claimId,
    {
      method: "GET",
      headers: headers,
    }
  ).then((response) => response.json());
}

export default function uploadFiles(files, claimId, token) {
  files.forEach((file) => {
    getSignedUrl(file.name, claimId, token).then((signedUrl) => {
      console.log("Signed URL", signedUrl);
      uploadFile(file, signedUrl).then((response) => {
        if (response.ok) {
          console.log("File uploaded successfully");
        } else {
          console.log("File upload failed");
        }
      });
    });
  });
}

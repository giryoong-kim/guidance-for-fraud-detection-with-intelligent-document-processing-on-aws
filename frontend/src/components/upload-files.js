// Javascript to upload files from local to S3 bucket using presigned URLs

import { API_ENDPOINT } from "../common/constants";


async function uploadFile(file, signedUrl) {
  try {
    console.log("Uploading file to S3", file);
    const response = await fetch(signedUrl.uploadURL, {
      method: "PUT",
      headers: {
        "Content-Type": "application/octet-stream",
      },
      body: file,
    });
    
    if (!response.ok) {
      throw new Error(`Upload failed! status: ${response.status}`);
    }
    
    return response;
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
}

async function getSignedUrl(file, claimId, token) {
  try {
    const headers = {
      'Authorization': token.token,
      'Content-Type': 'application/json',
    };
    console.log("Getting signed URL for file", file);
    console.debug("Token", token.token);
    
    const response = await fetch(
      API_ENDPOINT+"/get-presigned-post-url?file=" +
        file +
        "&claim_id=" +
        claimId,
      {
        method: "GET",
        headers: headers,
      }
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error getting signed URL:', error);
    throw error;
  }
}

export default async function uploadFiles(files, claimId, token) {
  const uploadPromises = files.map(async (file) => {
    try {
      const signedUrl = await getSignedUrl(file.name, claimId, token);
      console.log("Signed URL", signedUrl);
      
      const response = await uploadFile(file, signedUrl);
      console.log("File uploaded successfully");
      return { file: file.name, success: true };
    } catch (error) {
      console.error("File upload failed for", file.name, error);
      return { file: file.name, success: false, error: error.message };
    }
  });

  return await Promise.all(uploadPromises);
}

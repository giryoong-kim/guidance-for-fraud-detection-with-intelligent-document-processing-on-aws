// Javascript to upload files from local to S3 bucket using presigned URLs or proxy

import { API_ENDPOINT } from "../common/constants";

async function uploadFile(file, signedUrl) {
  try {
    console.log("Uploading file to S3 via presigned URL", file.name);

    // Remove the incorrect CORS header - this should not be set by the client
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

    console.log("File uploaded successfully via presigned URL");
    return response;
  } catch (error) {
    console.error("Error uploading file via presigned URL:", error);
    throw error;
  }
}

async function uploadFileViaProxy(file, claimId, token) {
  try {
    console.log("Uploading file via proxy", file.name);

    // Convert file to base64 for simpler handling
    const fileBuffer = await file.arrayBuffer();
    const base64File = btoa(String.fromCharCode(...new Uint8Array(fileBuffer)));

    const payload = {
      fileName: file.name,
      fileContent: base64File,
      claimId: claimId,
      contentType: file.type || "application/octet-stream",
    };

    const response = await fetch(`${API_ENDPOINT}/upload-file`, {
      method: "POST",
      headers: {
        Authorization: token.token,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Proxy upload failed! status: ${response.status}`);
    }

    console.log("File uploaded successfully via proxy");
    return response;
  } catch (error) {
    console.error("Error uploading file via proxy:", error);
    throw error;
  }
}

async function getSignedUrl(file, claimId, token) {
  try {
    const headers = {
      Authorization: token.token,
      "Content-Type": "application/json",
    };
    console.log("Getting signed URL for file", file);
    console.debug("Token", token.token);

    const response = await fetch(
      API_ENDPOINT +
        "/get-presigned-post-url?file=" +
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
    console.error("Error getting signed URL:", error);
    throw error;
  }
}

export default async function uploadFiles(files, claimId, token) {
  const uploadPromises = files.map(async (file) => {
    try {
      // First, try the presigned URL approach
      try {
        const signedUrl = await getSignedUrl(file.name, claimId, token);
        console.log("Signed URL obtained:", signedUrl);

        await uploadFile(file, signedUrl);
        return { file: file.name, success: true, method: "presigned" };
      } catch (presignedError) {
        console.warn(
          "Presigned URL upload failed, trying proxy method:",
          presignedError
        );

        // Fallback to proxy upload if presigned URL fails
        await uploadFileViaProxy(file, claimId, token);
        return { file: file.name, success: true, method: "proxy" };
      }
    } catch (error) {
      console.error("All upload methods failed for", file.name, error);
      return {
        file: file.name,
        success: false,
        error: error.message,
        method: "failed",
      };
    }
  });

  const results = await Promise.all(uploadPromises);

  // Log summary
  const successful = results.filter((r) => r.success);
  const failed = results.filter((r) => !r.success);

  console.log(
    `Upload summary: ${successful.length} successful, ${failed.length} failed`
  );
  if (successful.length > 0) {
    console.log(
      "Successful uploads:",
      successful.map((r) => `${r.file} (${r.method})`)
    );
  }
  if (failed.length > 0) {
    console.log(
      "Failed uploads:",
      failed.map((r) => r.file)
    );
  }

  return results;
}

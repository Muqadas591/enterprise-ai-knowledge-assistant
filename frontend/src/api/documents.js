import apiClient from "./client";

export async function getDocuments() {
  const response = await apiClient.get("/documents");

  return response.data;
}

///export async function getDocument(documentId) {
 // const response = await apiClient.get(
 //   `/documents/${documentId}`
 // );

 // return response.data;
///}
export async function getDocumentSource(
  documentId,
  chunkIndex
) {
  const response = await apiClient.get(
    `/documents/${documentId}/chunks/${chunkIndex}`
  );

  return response.data;
}

export async function uploadDocument(file, onUploadProgress) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await apiClient.post(
    "/documents/upload",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },

      onUploadProgress: (progressEvent) => {
        if (!progressEvent.total) return;

        const percentage = Math.round(
          (progressEvent.loaded * 100) /
            progressEvent.total
        );

        if (onUploadProgress) {
          onUploadProgress(percentage);
        }
      },
    }
  );

  return response.data;
}

export async function deleteDocument(documentId) {
  const response = await apiClient.delete(
    `/documents/${documentId}`
  );

  return response.data;
}
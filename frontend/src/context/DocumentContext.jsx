import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  getDocuments,
  uploadDocument,
  deleteDocument,
} from "../api/documents";

const DocumentContext = createContext(null);

export function DocumentProvider({ children }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState("");

  async function loadDocuments() {
    const token = localStorage.getItem("access_token");
    if (!token) return; // Skip API call if user is not logged in

    try {
      setLoading(true);
      setError("");

      const data = await getDocuments();
      setDocuments(data);
    } catch (error) {
      console.error("Failed to load documents:", error);
      setError("Unable to load documents.");
    } finally {
      setLoading(false);
    }
  }

  async function addDocument(file) {
    try {
      setUploading(true);
      setUploadProgress(0);
      setError("");

      const document = await uploadDocument(file, (progress) => {
        setUploadProgress(progress);
      });

      setDocuments((previous) => [document, ...previous]);
      return document;
    } catch (error) {
      console.error("Document upload failed:", error);
      const detail = error.response?.data?.detail;
      setError(detail || "Document upload failed.");
      throw error;
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }

  async function removeDocument(documentId) {
    try {
      setError("");
      await deleteDocument(documentId);

      setDocuments((previous) =>
        previous.filter((document) => document.id !== documentId)
      );
    } catch (error) {
      console.error("Document deletion failed:", error);
      setError("Unable to delete document.");
      throw error;
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  return (
    <DocumentContext.Provider
      value={{
        documents,
        loading,
        uploading,
        uploadProgress,
        error,
        loadDocuments,
        addDocument,
        removeDocument,
      }}
    >
      {children}
    </DocumentContext.Provider>
  );
}

export function useDocuments() {
  return useContext(DocumentContext);
}
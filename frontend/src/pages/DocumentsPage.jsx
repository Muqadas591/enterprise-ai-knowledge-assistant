import {
  FileText,
  RefreshCw,
} from "lucide-react";

import DocumentUpload from "../components/documents/DocumentUpload";
import DocumentList from "../components/documents/DocumentList";

import { useDocuments } from "../context/DocumentContext";
import DocumentStats from "../components/documents/DocumentStats";
export default function DocumentsPage() {
  const {
    documents,
    loading,
    error,
    loadDocuments,
    removeDocument,
  } = useDocuments();

  async function handleDelete(documentId) {
    const confirmed =
      window.confirm(
        "Delete this document? This will remove it from the knowledge base."
      );

    if (!confirmed) return;

    try {
      await removeDocument(documentId);
    } catch {
      // Context handles error.
    }
  }

  return (
    <div className="documents-page">
      <header className="documents-header">
        <div>
          <div className="page-title-row">
            <FileText size={23} />

            <h1>Documents</h1>
          </div>

          <p>
            Manage the documents available
            to your enterprise AI knowledge base.
          </p>
        </div>

        <DocumentUpload />
        <DocumentStats
  documents={documents}
/>
<section className="document-toolbar"></section>
      </header>

      {error && (
        <div className="document-error">
          {error}
        </div>
      )}

      <section className="document-toolbar">
        <div>
          <strong>
            {documents.length}
          </strong>{" "}
          document
          {documents.length !== 1
            ? "s"
            : ""}
        </div>

        <button
          className="refresh-documents"
          onClick={loadDocuments}
          disabled={loading}
        >
          <RefreshCw
            size={16}
            className={
              loading
                ? "refresh-spinning"
                : ""
            }
          />

          Refresh
        </button>
      </section>

      {loading ? (
        <div className="documents-loading">
          Loading documents...
        </div>
      ) : (
        <DocumentList
          documents={documents}
          onDelete={handleDelete}
        />
      )}
    </div>
  );
}
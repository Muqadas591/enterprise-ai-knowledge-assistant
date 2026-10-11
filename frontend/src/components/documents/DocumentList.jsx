import DocumentCard from "./DocumentCard";

export default function DocumentList({
  documents,
  onDelete,
}) {
  if (!documents.length) {
    return (
      <div className="document-empty">
        <div className="document-empty-icon">
          📄
        </div>

        <h3>No documents yet</h3>

        <p>
          Upload your organization's documents
          to make them available to the AI assistant.
        </p>
      </div>
    );
  }

  return (
    <div className="document-list">
      {documents.map((document) => (
        <DocumentCard
          key={document.id}
          document={document}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
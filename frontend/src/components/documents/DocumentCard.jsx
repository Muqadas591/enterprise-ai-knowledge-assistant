import {
  FileText,
  Trash2,
} from "lucide-react";

import DocumentStatus from "./DocumentStatus";

export default function DocumentCard({
  document,
  onDelete,
}) {
  const fileSize =
    document.file_size || 0;

  const sizeInKB =
    fileSize / 1024;

  const formattedSize =
    sizeInKB >= 1024
      ? `${(sizeInKB / 1024).toFixed(1)} MB`
      : `${sizeInKB.toFixed(1)} KB`;

  return (
    <div className="document-card">
      <div className="document-icon">
        <FileText size={22} />
      </div>

      <div className="document-main">
        <div className="document-name">
          {document.filename}
        </div>

        <div className="document-meta">
          <span>
            {document.file_type?.toUpperCase()}
          </span>

          <span>•</span>

          <span>
            {formattedSize}
          </span>

          {document.page_count && (
            <>
              <span>•</span>

              <span>
                {document.page_count} pages
              </span>
            </>
          )}
        </div>
      </div>

      <div className="document-actions">
        <DocumentStatus
          status={document.status}
        />

        <button
          className="document-delete-button"
          onClick={() =>
            onDelete(document.id)
          }
          title="Delete document"
        >
          <Trash2 size={17} />
        </button>
      </div>
    </div>
  );
}
import { useEffect, useState } from "react";

import {
  X,
  FileText,
  ExternalLink,
} from "lucide-react";

import { getDocumentSource } from "../../api/documents";

export default function SourceViewer({
  source,
  onClose,
}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

 useEffect(() => {
  if (!source) return;

  if (source.content) {
    setData(source);
    setLoading(false);
    return;
  }

  async function loadSource() {
      try {
        setLoading(true);
        setError("");

        const result =
          await getDocumentSource(
            source.document_id,
            source.chunk_index
          );

        setData(result);
      } catch (error) {
        console.error(error);

        setError(
          "Unable to load source content."
        );
      } finally {
        setLoading(false);
      }
    }

    loadSource();
  }, [source]);

  if (!source) {
    return null;
  }

  return (
    <div
      className="source-overlay"
      onClick={onClose}
    >
      <aside
        className="source-viewer"
        onClick={(event) =>
          event.stopPropagation()
        }
      >
        <header className="source-viewer-header">
          <div className="source-viewer-title">
            <FileText size={19} />

            <div>
              <strong>
                Source
              </strong>

              <span>
                {source.filename}
              </span>
            </div>
          </div>

          <button
            className="source-close"
            onClick={onClose}
          >
            <X size={19} />
          </button>
        </header>

        {loading && (
          <div className="source-viewer-loading">
            Loading source...
          </div>
        )}

        {error && (
          <div className="source-viewer-error">
            {error}
          </div>
        )}

        {data && !loading && (
          <>
            <div className="source-metadata">
              <div>
                <span>Document</span>
                <strong>
                  {data.filename}
                </strong>
              </div>

              {data.page_number && (
                <div>
                  <span>Page</span>
                  <strong>
                    {data.page_number}
                  </strong>
                </div>
              )}

              <div>
                <span>Chunk</span>
                <strong>
                  {data.chunk_index}
                </strong>
              </div>

              {data.section_title && (
                <div>
                  <span>Section</span>
                  <strong>
                    {data.section_title}
                  </strong>
                </div>
              )}
            </div>

            <div className="source-content">
              <div className="source-content-label">
                Retrieved evidence
              </div>

              <div className="source-highlight">
                {data.content}
              </div>
            </div>
          </>
        )}

        <footer className="source-viewer-footer">
          <span>
            Retrieved from your enterprise
            knowledge base
          </span>

          <ExternalLink size={14} />
        </footer>
      </aside>
    </div>
  );
}
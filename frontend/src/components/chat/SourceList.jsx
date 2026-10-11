import { useState } from "react";

import { ExternalLink } from "lucide-react";

import SourceViewer from "./SourceViewer";

export default function SourceList({
  sources = [],
}) {
  const [selectedSource, setSelectedSource] =
    useState(null);

  if (!sources.length) {
    return null;
  }

  return (
    <>
      <div className="source-list">
        <div className="source-heading">
          Sources
        </div>

        {sources.map((source, index) => (
          <button
            className="source-card"
            key={`${source.document_id}-${source.chunk_index}-${index}`}
            onClick={() =>
              setSelectedSource(source)
            }
          >
            <div className="source-card-main">
              <div className="source-title">
                {source.filename}
              </div>

              <div className="source-meta">
                {source.page_number
                  ? `Page ${source.page_number}`
                  : "Document source"}

                {source.section_title &&
                  ` · ${source.section_title}`}
              </div>
            </div>

            <ExternalLink size={14} />
          </button>
        ))}
      </div>

      {selectedSource && (
        <SourceViewer
          source={selectedSource}
          onClose={() =>
            setSelectedSource(null)
          }
        />
      )}
    </>
  );
}
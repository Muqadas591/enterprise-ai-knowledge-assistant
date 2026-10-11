import {
  Upload,
  FileText,
} from "lucide-react";

import { useRef, useState } from "react";

import { useDocuments } from "../../context/DocumentContext";

const ALLOWED_TYPES = [
  ".pdf",
  ".docx",
  ".txt",
];

const MAX_SIZE =
  20 * 1024 * 1024;

export default function DocumentUpload() {
  const fileInputRef = useRef(null);

  const {
    addDocument,
    uploading,
    uploadProgress,
  } = useDocuments();

  const [localError, setLocalError] =
    useState("");

  async function handleFile(file) {
    if (!file) return;

    setLocalError("");

    const extension =
      "." +
      file.name
        .split(".")
        .pop()
        .toLowerCase();

    if (!ALLOWED_TYPES.includes(extension)) {
      setLocalError(
        "Only PDF, DOCX, and TXT files are supported."
      );

      return;
    }

    if (file.size > MAX_SIZE) {
      setLocalError(
        "File size must not exceed 20 MB."
      );

      return;
    }

    try {
      await addDocument(file);
    } catch {
      // Context handles the error.
    }
  }

  function handleInputChange(event) {
    const file =
      event.target.files?.[0];

    handleFile(file);

    event.target.value = "";
  }

  return (
    <div className="document-upload">
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={handleInputChange}
        hidden
      />

      <button
        className="upload-button"
        onClick={() =>
          fileInputRef.current?.click()
        }
        disabled={uploading}
      >
        <Upload size={18} />

        {uploading
          ? `Uploading ${uploadProgress}%`
          : "Upload document"}
      </button>

      <div className="upload-help">
        <FileText size={15} />

        <span>
          PDF, DOCX or TXT · Maximum 20 MB
        </span>
      </div>

      {uploading && (
        <div className="upload-progress">
          <div
            className="upload-progress-bar"
            style={{
              width: `${uploadProgress}%`,
            }}
          />
        </div>
      )}

      {localError && (
        <div className="upload-error">
          {localError}
        </div>
      )}
    </div>
  );
}
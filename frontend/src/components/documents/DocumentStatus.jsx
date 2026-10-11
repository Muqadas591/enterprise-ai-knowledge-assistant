export default function DocumentStatus({
  status,
}) {
  const normalizedStatus =
    status?.toLowerCase() || "unknown";

  const labels = {
    processing: "Processing",
    processed: "Ready",
    failed: "Failed",
  };

  const label =
    labels[normalizedStatus] ||
    normalizedStatus;

  return (
    <span
      className={`document-status status-${normalizedStatus}`}
    >
      <span className="status-dot" />
      {label}
    </span>
  );
}
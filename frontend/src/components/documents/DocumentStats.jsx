export default function DocumentStats({
  documents,
}) {
  const total = documents.length;

  const ready = documents.filter(
    (document) =>
      document.status === "processed"
  ).length;

  const processing = documents.filter(
    (document) =>
      document.status === "processing"
  ).length;

  const failed = documents.filter(
    (document) =>
      document.status === "failed"
  ).length;

  const stats = [
    {
      label: "Total",
      value: total,
    },
    {
      label: "Ready",
      value: ready,
    },
    {
      label: "Processing",
      value: processing,
    },
    {
      label: "Failed",
      value: failed,
    },
  ];

  return (
    <div className="document-stats">
      {stats.map((stat) => (
        <div
          className="document-stat"
          key={stat.label}
        >
          <span>{stat.label}</span>
          <strong>{stat.value}</strong>
        </div>
      ))}
    </div>
  );
}
import {
  ShieldCheck,
  ShieldAlert,
  Shield,
} from "lucide-react";

export default function AnswerQualityBadge({ quality }) {
  if (!quality) {
    return null;
  }

  const {
    confidence,
    citation_quality,
    source_count,
  } = quality;

  const Icon =
    confidence === "high"
      ? ShieldCheck
      : confidence === "medium"
        ? Shield
        : ShieldAlert;

  return (
    <div
      className={`answer-quality quality-${confidence}`}
      title={`Based on ${source_count} retrieved source(s)`}
    >
      <Icon size={14} />

      <span>
        {confidence === "high"
          ? "Strong evidence"
          : confidence === "medium"
            ? "Moderate evidence"
            : "Limited evidence"}
      </span>

      {citation_quality !== "none" && (
        <span className="quality-sources">
          {source_count} source
          {source_count !== 1 ? "s" : ""}
        </span>
      )}
    </div>
  );
}

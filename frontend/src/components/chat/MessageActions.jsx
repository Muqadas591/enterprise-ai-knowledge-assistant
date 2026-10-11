import { useState } from "react";
import {
  Check,
  Copy,
  RefreshCw,
  ThumbsDown,
  ThumbsUp,
} from "lucide-react";

export default function MessageActions({
  content,
  onRegenerate,
  onFeedback,
  disabled = false,
}) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      onFeedback?.("copy-failed");
    }
  }

  return (
    <div className="message-actions" aria-label="Answer actions">
      <button type="button" onClick={handleCopy} title="Copy answer" aria-label="Copy answer">
        {copied ? <Check size={15} /> : <Copy size={15} />}
      </button>
      <button type="button" onClick={onRegenerate} title="Regenerate answer" aria-label="Regenerate answer" disabled={disabled}>
        <RefreshCw size={15} />
      </button>
      <button type="button" onClick={() => onFeedback?.("positive")} title="Helpful" aria-label="Helpful" disabled={disabled}>
        <ThumbsUp size={15} />
      </button>
      <button type="button" onClick={() => onFeedback?.("negative")} title="Not helpful" aria-label="Not helpful" disabled={disabled}>
        <ThumbsDown size={15} />
      </button>
    </div>
  );
}
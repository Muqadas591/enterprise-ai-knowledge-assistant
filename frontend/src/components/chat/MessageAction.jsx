import { useState } from "react";
import {
  Copy,
  Check,
  RefreshCw,
  ThumbsUp,
  ThumbsDown,
} from "lucide-react";

import { submitFeedback } from "../../api/qa";


export default function MessageActions({
  message,
  onRegenerate,
}) {
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [feedbackLoading, setFeedbackLoading] = useState(false);

  if (!message || message.role !== "assistant") {
    return null;
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(message.content);

      setCopied(true);

      setTimeout(() => {
        setCopied(false);
      }, 1500);
    } catch (error) {
      console.error("Copy failed:", error);
    }
  }

  async function handleFeedback(rating) {
    if (!message.id || feedbackLoading) {
      return;
    }

    try {
      setFeedbackLoading(true);

      await submitFeedback(
        message.id,
        rating
      );

      setFeedback(rating);
    } catch (error) {
      console.error(
        "Feedback submission failed:",
        error
      );
    } finally {
      setFeedbackLoading(false);
    }
  }

  return (
    <div className="message-actions">
      <button
        type="button"
        className={`message-action ${
          copied ? "active" : ""
        }`}
        onClick={handleCopy}
        title="Copy answer"
      >
        {copied ? (
          <Check size={15} />
        ) : (
          <Copy size={15} />
        )}
      </button>

      <button
        type="button"
        className="message-action"
        onClick={() => onRegenerate?.(message)}
        title="Regenerate answer"
      >
        <RefreshCw size={15} />
      </button>

      <button
        type="button"
        className={`message-action ${
          feedback === "up" ? "active" : ""
        }`}
        onClick={() => handleFeedback("up")}
        disabled={feedbackLoading}
        title="Helpful"
      >
        <ThumbsUp size={15} />
      </button>

      <button
        type="button"
        className={`message-action ${
          feedback === "down" ? "active" : ""
        }`}
        onClick={() => handleFeedback("down")}
        disabled={feedbackLoading}
        title="Not helpful"
      >
        <ThumbsDown size={15} />
      </button>
    </div>
  );
}
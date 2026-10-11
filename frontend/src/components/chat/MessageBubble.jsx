import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import AnswerQualityBadge from "./AnswerQualityBadge";
import MessageActions from "./MessageActions";
import SourceList from "./SourceList";

export default function MessageBubble({
  message,
  onRegenerate,
  onFeedback,
  isStreaming,
}) {
  const isUser = message.role === "user";

  return (
    <div
      className={`message-row ${
        isUser ? "message-user" : "message-assistant"
      }`}
    >
      <div className="message-bubble">
        <div className="message-role">
          {isUser ? "You" : "Enterprise AI"}
        </div>

        <div className="message-content">
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {message.role === "assistant" && message.quality && (
          <AnswerQualityBadge quality={message.quality} />
        )}

        {message.role === "assistant" &&
          message.sources?.length > 0 && (
            <SourceList sources={message.sources} />
          )}

        {!isUser && (
          <MessageActions
            content={message.content}
            onRegenerate={onRegenerate}
            onFeedback={onFeedback}
            disabled={isStreaming}
          />
        )}
      </div>
    </div>
  );
}

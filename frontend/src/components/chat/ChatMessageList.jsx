import MessageBubble from "./MessageBubble";
import SourceList from "./SourceList";

export default function ChatMessageList({
  messages,
  loading,
  isStreaming,
  streamingMessage,
  streamingSources,
  messagesEndRef,
  onRegenerate,
  onFeedback,
}) {
  if (messages.length === 0 && !loading && !isStreaming) {
    return (
      <div className="chat-empty-state">
        <div className="chat-empty-icon">✦</div>

        <h2>How can I help you?</h2>

        <p>
          Ask questions about your organization's
          documents, policies, procedures, and knowledge.
        </p>
        <div ref={messagesEndRef} />
      </div>
    );
  }

  return (
    <div className="chat-messages">
      {messages.map((message, index) => (
        <MessageBubble
          key={message.id || index}
          message={message}
          onRegenerate={() => onRegenerate?.(message, index)}
          onFeedback={(rating) => onFeedback?.(index, rating)}
          isStreaming={isStreaming}
        />
      ))}

      {isStreaming && (
        <div className="message-row message-assistant streaming-message">
          <div className="message-bubble">
            <div className="message-role">Enterprise AI</div>
            <div className="message-content">
              {streamingMessage || (
                <div className="typing-indicator" aria-label="Generating answer">
                  <span />
                  <span />
                  <span />
                </div>
              )}
              {streamingMessage && <span className="streaming-cursor">▌</span>}
            </div>
          </div>
        </div>
      )}

      {isStreaming && streamingSources?.length > 0 && (
        <SourceList sources={streamingSources} />
      )}

      {loading && (
        <div className="message-row message-assistant">
          <div className="message-bubble loading-message">
            <div className="message-role">
              Enterprise AI
            </div>

            <div className="typing-indicator">
              <span />
              <span />
              <span />
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}

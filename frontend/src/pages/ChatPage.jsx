import { useEffect, useRef, useState } from "react";
import { Send, Square } from "lucide-react";
import { getConversation } from "../api/conversations";
import { streamQuestion } from "../api/qa";

import { useConversations } from "../context/ConversationContext";

import ChatMessageList from "../components/chat/ChatMessageList";
import GenerationStatus from "../components/chat/GenerationStatus";

export default function ChatPage() {
  const {
    activeConversationId,
    conversations,
    patchConversation,
  } = useConversations();

  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState("");
  const [streamingSources, setStreamingSources] = useState([]);
  const [streamQuality, setStreamQuality] = useState(null);
  const streamingTextRef = useRef("");
  const streamingSourcesRef = useRef([]);
  const streamingQualityRef = useRef(null);
  const abortControllerRef = useRef(null);
  const lastRequestRef = useRef(null);
  const messagesEndRef = useRef(null);
  const [question, setQuestion] = useState("");
  const [loadingConversation, setLoadingConversation] =
    useState(false);
  const [error, setError] = useState("");

  const activeConversation = conversations.find(
    (conversation) =>
      conversation.id === activeConversationId
  );

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingMessage]);

  useEffect(() => {
    if (!activeConversationId) {
      setMessages([]);
      return;
    }

    loadConversation(activeConversationId);
  }, [activeConversationId]);

  async function loadConversation(conversationId) {
    try {
      setLoadingConversation(true);
      setError("");

      const conversation =
        await getConversation(conversationId);

      setMessages(conversation.messages || []);
    } catch (error) {
      console.error(error);

      setError(
        "Unable to load this conversation."
      );
    } finally {
      setLoadingConversation(false);
    }
  }

  async function handleSendMessage(event, options = {}) {
    event?.preventDefault();
    const trimmedQuestion = (options.question ?? question).trim();

    if (!trimmedQuestion || isStreaming) return;

    if (!activeConversationId) {
      setError(
        "Please create a conversation first."
      );

      return;
    }

    lastRequestRef.current = {
      question: trimmedQuestion,
      options,
    };

    if (options.appendUser !== false) {
      setMessages((previous) => [
        ...previous,
        { role: "user", content: trimmedQuestion },
      ]);
      setQuestion("");
    } else if (Number.isInteger(options.replaceFromIndex)) {
      setMessages((previous) => previous.slice(0, options.replaceFromIndex));
    }

    setIsStreaming(true);
    setStreamingMessage("");
    setStreamingSources([]);
    setStreamQuality(null);
    streamingTextRef.current = "";
    streamingSourcesRef.current = [];
    streamingQualityRef.current = null;
    setError("");
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      await streamQuestion({
        question: trimmedQuestion,
        conversationId: activeConversationId,
        topK: 5,
        regenerate: options.regenerate || false,
        regenerateMessageId: options.messageId,
        signal: controller.signal,
        onToken: (token) => {
          streamingTextRef.current += token;
          setStreamingMessage(streamingTextRef.current);
        },
        onSources: (sources) => {
          streamingSourcesRef.current = sources;
          setStreamingSources(sources);
        },
        onQuality: (quality) => {
          streamingQualityRef.current = quality;
          setStreamQuality(quality);
        },
        onDone: (data) => {
          const finalAnswer = streamingTextRef.current;
          const finalSources = streamingSourcesRef.current;
          const finalQuality =
            data.quality || streamingQualityRef.current;

          setMessages((previous) => [
            ...(Number.isInteger(options.replaceFromIndex)
              ? previous.slice(0, options.replaceFromIndex)
              : previous),
            {
              id: data.assistant_message_id,
              role: "assistant",
              content: finalAnswer,
              sources: finalSources,
              quality: finalQuality,
              model: data.model,
            },
          ]);

          if (data.conversation_title) {
            patchConversation?.(activeConversationId, {
              title: data.conversation_title,
            });
          }

          streamingTextRef.current = "";
          streamingSourcesRef.current = [];
          streamingQualityRef.current = null;
          setStreamingMessage("");
          setStreamingSources([]);
          setStreamQuality(null);
          setIsStreaming(false);
          lastRequestRef.current = null;
        },
        onError: (error) =>
          setError(error?.message || String(error)),
      });
    } catch (error) {
      if (error.name !== "AbortError") {
        setError(error.message || "Something went wrong.");
      }
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  }

  function handleStopGeneration() {
    abortControllerRef.current?.abort();
    setIsStreaming(false);
    setStreamingMessage("");
    setStreamingSources([]);
    setStreamQuality(null);
    streamingTextRef.current = "";
    streamingSourcesRef.current = [];
    streamingQualityRef.current = null;
  }

  function handleRetry() {
    const lastRequest = lastRequestRef.current;
    if (!lastRequest || isStreaming) return;
    setError("");
    handleSendMessage(undefined, {
      ...lastRequest.options,
      question: lastRequest.question,
      appendUser: false,
    });
  }

  function findPreviousUserMessage(messageIndex) {
    for (let index = messageIndex - 1; index >= 0; index -= 1) {
      if (messages[index]?.role === "user") return messages[index];
    }

    return null;
  }

  async function handleRegenerate(message, messageIndex) {
    if (isStreaming) return;
    const previousUserMessage = findPreviousUserMessage(messageIndex);
    if (!previousUserMessage) return;

    await handleSendMessage(undefined, {
      question: previousUserMessage.content,
      appendUser: false,
      regenerate: true,
      messageId: message.id,
      replaceFromIndex: messageIndex,
    });
  }

  function handleFeedback(messageIndex, rating) {
    if (rating === "copy-failed") return;
    setMessages((previous) =>
      previous.map((message, index) =>
        index === messageIndex ? { ...message, feedback: rating } : message,
      ),
    );
  }

  return (
    <div className="chat-page">
      <header className="chat-header">
        <div>
          <h1>
            {activeConversation?.title ||
              "Enterprise Knowledge Assistant"}
          </h1>

          <p>
            Ask questions and retrieve verified
            information from your organization's knowledge base.
          </p>
        </div>
      </header>

      {error && (
        <div className="chat-error">
          <div>
            <strong>Something went wrong</strong>
            <p>{error}</p>
          </div>
          <button type="button" onClick={handleRetry}>
            Try again
          </button>
        </div>
      )}

      <div className="chat-content">
        {loadingConversation ? (
          <div className="chat-loading">
            Loading conversation...
          </div>
        ) : (
          <ChatMessageList
            messages={messages}
            loading={loadingConversation}
            isStreaming={isStreaming}
            streamingMessage={streamingMessage}
            streamingSources={streamingSources}
            messagesEndRef={messagesEndRef}
            onRegenerate={handleRegenerate}
            onFeedback={handleFeedback}
          />
        )}
      </div>

      <GenerationStatus
        isStreaming={isStreaming}
        onStop={handleStopGeneration}
      />

      <form
        className="chat-input-container"
        onSubmit={handleSendMessage}
      >
        <textarea
          value={question}
          onChange={(event) =>
            setQuestion(event.target.value)
          }
          placeholder="Ask a question about your organization's knowledge..."
          rows={1}
          disabled={isStreaming || !activeConversationId}
          onKeyDown={(event) => {
            if (
              event.key === "Enter" &&
              !event.shiftKey
            ) {
              event.preventDefault();

              handleSendMessage(event);
            }
          }}
        />

        <button
          type="submit"
          disabled={!isStreaming && (!question.trim() || !activeConversationId)}
          onClick={isStreaming ? handleStopGeneration : undefined}
          aria-label={isStreaming ? "Stop generation" : "Send message"}
        >
          {isStreaming ? <Square size={16} fill="currentColor" /> : <Send size={18} />}
        </button>
      </form>
    </div>
  );
}

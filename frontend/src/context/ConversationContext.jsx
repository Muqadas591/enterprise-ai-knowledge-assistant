import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  getConversations,
  createConversation,
  deleteConversation,
  updateConversation,
  archiveConversation,
  searchConversations,
} from "../api/conversations";
import { withRetry } from "../utils/retry";

const ConversationContext = createContext(null);

export function ConversationProvider({ children }) {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadConversations() {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    try {
      setLoading(true);
      setError("");
      const data = await withRetry(() => getConversations());
      setConversations(data);
    } catch (err) {
      console.error("Failed to load conversations:", err);
      setError("Unable to load conversations.");
    } finally {
      setLoading(false);
    }
  }

  async function newConversation(title = "New Conversation") {
    try {
      setError("");
      const created = await createConversation(title);
      setConversations((prev) => [created, ...prev]);
      setActiveConversationId(created.id);
      setSearchQuery("");
      return created;
    } catch (err) {
      console.error("Failed to create conversation:", err);
      setError("Unable to create conversation.");
      throw err;
    }
  }

  async function removeConversation(conversationId) {
    try {
      setError("");
      await deleteConversation(conversationId);
      setConversations((prev) =>
        prev.filter((conv) => conv.id !== conversationId)
      );

      if (activeConversationId === conversationId) {
        setActiveConversationId(null);
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
      setError("Unable to delete conversation.");
      throw err;
    }
  }

  async function renameConversation(conversationId, title) {
    const updated = await updateConversation(conversationId, { title });
    setConversations((prev) =>
      prev.map((conversation) =>
        conversation.id === conversationId ? updated : conversation
      )
    );
    return updated;
  }

  async function archiveConversationById(conversationId) {
    await archiveConversation(conversationId);
    setConversations((prev) =>
      prev.filter((conversation) => conversation.id !== conversationId)
    );
    if (activeConversationId === conversationId) {
      setActiveConversationId(null);
    }
  }

  function patchConversation(conversationId, updates) {
    setConversations((prev) =>
      prev.map((conversation) =>
        conversation.id === conversationId
          ? { ...conversation, ...updates }
          : conversation
      )
    );
  }

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) return undefined;

    const timeout = setTimeout(async () => {
      try {
        setLoading(true);
        setError("");

        if (!searchQuery.trim()) {
          const data = await withRetry(() => getConversations());
          setConversations(data);
          return;
        }

        const results = await searchConversations(searchQuery);
        setConversations(results);
      } catch (err) {
        console.error("Failed to load conversations:", err);
        setError(
          searchQuery.trim()
            ? "Unable to search conversations."
            : "Unable to load conversations."
        );
      } finally {
        setLoading(false);
      }
    }, 250);

    return () => clearTimeout(timeout);
  }, [searchQuery]);

  return (
    <ConversationContext.Provider
      value={{
        conversations,
        activeConversationId,
        searchQuery,
        loading,
        error,
        setActiveConversationId,
        setSearchQuery,
        loadConversations,
        newConversation,
        removeConversation,
        renameConversation,
        archiveConversationById,
        patchConversation,
      }}
    >
      {children}
    </ConversationContext.Provider>
  );
}

export function useConversations() {
  return useContext(ConversationContext);
}

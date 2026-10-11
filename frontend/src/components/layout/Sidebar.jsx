import {
  Files,
  MessageSquarePlus,
  MessageSquare,
} from "lucide-react";

import { NavLink } from "react-router-dom";

import { useConversations } from "../../context/ConversationContext";
import ConversationMenu from "../conversations/ConversationMenu";
import ConversationSearch from "../conversations/ConversationSearch";

function startOfDay(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function groupConversationsByDate(conversations) {
  const now = new Date();
  const today = startOfDay(now);
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  const groups = [
    { label: "Today", items: [] },
    { label: "Yesterday", items: [] },
    { label: "Older", items: [] },
  ];

  for (const conversation of conversations) {
    const stamp = new Date(
      conversation.updated_at || conversation.created_at
    );
    const day = startOfDay(stamp);

    if (day.getTime() === today.getTime()) {
      groups[0].items.push(conversation);
    } else if (day.getTime() === yesterday.getTime()) {
      groups[1].items.push(conversation);
    } else {
      groups[2].items.push(conversation);
    }
  }

  return groups.filter((group) => group.items.length > 0);
}

export default function Sidebar() {
  const {
    conversations,
    activeConversationId,
    searchQuery,
    setActiveConversationId,
    setSearchQuery,
    newConversation,
    removeConversation,
    renameConversation,
    archiveConversationById,
  } = useConversations();

  async function handleNewConversation() {
    await newConversation().catch(() => {});
  }

  async function handleRename(conversation) {
    const nextTitle = window.prompt(
      "Rename conversation",
      conversation.title || "New Conversation"
    );

    if (!nextTitle?.trim()) return;

    await renameConversation(conversation.id, nextTitle.trim()).catch(
      () => {}
    );
  }

  async function handleArchive(conversation) {
    await archiveConversationById(conversation.id).catch(() => {});
  }

  async function handleDelete(conversation) {
    const confirmed = window.confirm("Delete this conversation?");
    if (!confirmed) return;
    await removeConversation(conversation.id).catch(() => {});
  }

  const groupedConversations = groupConversationsByDate(conversations);

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Enterprise AI</h2>
      </div>

      <button
        className="new-chat-button"
        onClick={handleNewConversation}
      >
        <MessageSquarePlus size={18} />
        New conversation
      </button>

      <ConversationSearch
        value={searchQuery}
        onChange={setSearchQuery}
      />

      <nav className="sidebar-navigation">
        <NavLink
          to="/chat"
          className={({ isActive }) =>
            `sidebar-nav-item ${isActive ? "active" : ""}`
          }
        >
          <MessageSquare size={17} />
          Chat
        </NavLink>

        <NavLink
          to="/documents"
          className={({ isActive }) =>
            `sidebar-nav-item ${isActive ? "active" : ""}`
          }
        >
          <Files size={17} />
          Documents
        </NavLink>
      </nav>

      <div className="conversation-section">
        {conversations.length === 0 ? (
          <div className="empty-conversations">
            <MessageSquare size={18} />
            <span>
              {searchQuery.trim()
                ? "No matching conversations"
                : "No conversations yet"}
            </span>
          </div>
        ) : (
          <div className="conversation-list">
            {groupedConversations.map((group) => (
              <div key={group.label} className="conversation-group">
                <p className="sidebar-section-heading">{group.label}</p>

                {group.items.map((conversation) => {
                  const isActive =
                    conversation.id === activeConversationId;

                  return (
                    <div
                      key={conversation.id}
                      className={`conversation-item ${
                        isActive ? "active" : ""
                      }`}
                      onClick={() =>
                        setActiveConversationId(conversation.id)
                      }
                    >
                      <MessageSquare size={17} />

                      <span className="conversation-title">
                        {conversation.title || "New Conversation"}
                      </span>

                      <ConversationMenu
                        conversation={conversation}
                        onRename={handleRename}
                        onArchive={handleArchive}
                        onDelete={handleDelete}
                      />
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}

import {
  Archive,
  MoreVertical,
  Pencil,
  Trash2,
} from "lucide-react";

import { useState } from "react";


export default function ConversationMenu({
  conversation,
  onRename,
  onArchive,
  onDelete,
}) {
  const [open, setOpen] = useState(false);

  if (!conversation) {
    return null;
  }

  return (
    <div className="conversation-menu">
      <button
        type="button"
        className="conversation-menu-trigger"
        onClick={(event) => {
          event.stopPropagation();
          setOpen(!open);
        }}
      >
        <MoreVertical size={16} />
      </button>

      {open && (
        <div
          className="conversation-menu-dropdown"
          onClick={(event) => event.stopPropagation()}
        >
          <button
            type="button"
            onClick={() => {
              setOpen(false);
              onRename?.(conversation);
            }}
          >
            <Pencil size={14} />
            Rename
          </button>

          <button
            type="button"
            onClick={() => {
              setOpen(false);
              onArchive?.(conversation);
            }}
          >
            <Archive size={14} />
            Archive
          </button>

          <button
            type="button"
            className="danger"
            onClick={() => {
              setOpen(false);
              onDelete?.(conversation);
            }}
          >
            <Trash2 size={14} />
            Delete
          </button>
        </div>
      )}

    </div>
  );
}
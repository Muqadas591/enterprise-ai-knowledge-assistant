import { Search, X } from "lucide-react";


export default function ConversationSearch({
  value,
  onChange,
}) {
  return (
    <div className="conversation-search">
      <Search size={16} />

      <input
        type="text"
        value={value}
        onChange={(event) =>
          onChange(event.target.value)
        }
        placeholder="Search conversations..."
      />

      {value && (
        <button
          type="button"
          onClick={() => onChange("")}
          aria-label="Clear search"
        >
          <X size={15} />
        </button>
      )}
    </div>
  );
}
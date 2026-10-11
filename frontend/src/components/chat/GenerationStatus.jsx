import { LoaderCircle } from "lucide-react";

export default function GenerationStatus({
  isStreaming,
  onStop,
}) {
  if (!isStreaming) {
    return null;
  }

  return (
    <div className="generation-status">
      <div className="generation-status-text">
        <LoaderCircle
          size={15}
          className="generation-spinner"
        />

        <span>Generating response...</span>
      </div>

      <button type="button" onClick={onStop}>
        Stop
      </button>
    </div>
  );
}

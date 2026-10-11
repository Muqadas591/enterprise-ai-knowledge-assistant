import apiClient from "./client";

export async function askQuestion({
  question,
  conversationId,
  topK = 5,
}) {
  const response = await apiClient.post("/qa/ask", {
    question,
    conversation_id: conversationId,
    top_k: topK,
  });

  return response.data;
}

export async function submitFeedback(messageId, rating, comment = null) {
  const normalizedRating =
    rating === "positive" ? "up" : rating === "negative" ? "down" : rating;
  const response = await apiClient.post(
    `/feedback/messages/${messageId}`,
    {
      rating: normalizedRating,
      comment,
    },
  );

  return response.data;
}

export async function streamQuestion({
  question,
  conversationId,
  topK = 5,
  regenerate = false,
  regenerateMessageId,
  onToken,
  onSources,
  onQuality,
  onDone,
  onError,
  signal,
}) {
  const token = localStorage.getItem("access_token");

  try {
    const response = await fetch(
      `${import.meta.env.VITE_API_BASE_URL}/qa/ask/stream`,
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
          ...(token
            ? {
                Authorization: `Bearer ${token}`,
              }
            : {}),
        },

        body: JSON.stringify({
          question,
          conversation_id: conversationId,
          top_k: topK,
          regenerate,
          regenerate_message_id: regenerateMessageId,
        }),

        signal,
      }
    );

    if (!response.ok) {
      let message = "Unable to generate the answer.";

      try {
        const data = await response.json();
        message = data.detail || message;
      } catch {
        // Keep generic message
      }

      throw new Error(message);
    }

    if (!response.body) {
      throw new Error(
        "Streaming is not supported by this browser."
      );
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });

      const events = buffer.split("\n\n");
      buffer = events.pop() || "";

      for (const event of events) {
        const line = event
          .split("\n")
          .find((line) => line.startsWith("data:"));

        if (!line) {
          continue;
        }

        const json = line.slice(5).trim();

        if (!json) {
          continue;
        }

        const payload = JSON.parse(json);

        switch (payload.type) {
          case "token":
            onToken?.(payload.data.text);
            break;

          case "sources":
            onSources?.(payload.data.sources || []);
            break;

          case "quality":
            onQuality?.(payload.data);
            break;

          case "done":
            onDone?.(payload.data);
            break;

          case "error":
            throw new Error(
              payload.data.message || "Generation failed."
            );
        }
      }
    }
  } catch (error) {
    if (error?.name === "AbortError") {
      return;
    }

    onError?.(error);
  }
}

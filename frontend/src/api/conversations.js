import apiClient from "./client";

export async function createConversation(title = "New Conversation") {
  const response = await apiClient.post("/conversations", {
    title,
  });

  return response.data;
}

export async function getConversations() {
  const response = await apiClient.get("/conversations");

  return response.data;
}

export async function getConversation(conversationId) {
  const response = await apiClient.get(
    `/conversations/${conversationId}`
  );

  return response.data;
}

export async function deleteConversation(conversationId) {
  await apiClient.delete(`/conversations/${conversationId}`);
}
export async function updateConversation(
  conversationId,
  data
) {
  const response = await apiClient.patch(
    `/conversations/${conversationId}`,
    data
  );

  return response.data;
}


export async function archiveConversation(
  conversationId
) {
  const response = await apiClient.post(
    `/conversations/${conversationId}/archive`
  );

  return response.data;
}


export async function searchConversations(
  query
) {
  const response = await apiClient.get(
    `/conversations/search`,
    {
      params: {
        q: query,
      },
    }
  );

  return response.data;
}
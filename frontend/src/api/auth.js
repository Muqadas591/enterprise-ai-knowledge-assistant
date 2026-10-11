import apiClient from "./client";

export async function registerUser(data) {
  const response = await apiClient.post("/auth/register", data);
  return response.data;
}

export async function loginUser(data) {
  const response = await apiClient.post("/auth/login", data);
  return response.data;
}

export async function requestPasswordReset(data) {
  const response = await apiClient.post("/auth/forgot-password", data);
  return response.data;
}

export async function resetPassword(data) {
  const response = await apiClient.post("/auth/reset-password", data);
  return response.data;
}

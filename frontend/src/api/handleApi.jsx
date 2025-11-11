import { API_BASE_URL } from "./config";

export async function handleApi(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const defaultHeaders = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  const response = await fetch(url, {
    ...options,
    headers: defaultHeaders,
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(`Erro: ${response.status}`);
  }

  return response.json();
}

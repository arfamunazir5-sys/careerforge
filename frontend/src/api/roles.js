import { API_BASE_URL } from "./client";

async function get(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

export const rolesApi = {
  getRoles: () => get("/roles"),
  simulate: () => get("/simulate-roles"),
};
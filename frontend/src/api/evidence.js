import { API_BASE_URL } from "./client";

export const evidenceApi = {
  submit: async (data) => {
    const response = await fetch(`${API_BASE_URL}/portfolio-evidence`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail || `Request failed: ${response.status}`);
    }
    return response.json();
  },
};
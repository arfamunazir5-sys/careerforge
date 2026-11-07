import { API_BASE_URL } from "./client";

async function call(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const error = new Error(errorBody.detail || `Request failed: ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return response.json();
}

export const weeklyApi = {
  getSummary: () => call("/week-summary"),
  nextWeek: (data) => call("/next-week", { method: "POST", body: JSON.stringify(data) }),
};
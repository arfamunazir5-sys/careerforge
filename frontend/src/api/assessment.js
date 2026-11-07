import { API_BASE_URL } from "./client";

async function call(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

export const assessmentApi = {
  getQuestions: () => call("/self-assessment/questions"),
  submit: (data) => call("/self-assessment", { method: "POST", body: JSON.stringify(data) }),
};
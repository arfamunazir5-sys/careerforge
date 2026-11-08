import { API_BASE_URL } from "./client";

export const resumeApi = {
  // Sends a PDF to the backend, which reads its text in memory (nothing is stored).
  extractText: async (file) => {
    const form = new FormData();
    form.append("file", file);
    const response = await fetch(`${API_BASE_URL}/extract-resume-text`, { method: "POST", body: form });
    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail || `Request failed: ${response.status}`);
    }
    return response.json();
  },
};
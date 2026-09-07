export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
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

// Treats a 404 as "nothing exists yet" instead of a real error —
// used for /plan, since "no plan generated yet" is a normal state.
async function requestAllowingMissing(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (response.status === 404) return null;
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

export const api = {
  getState: () => request("/state"),
  generatePlan: () => request("/generate-plan", { method: "POST" }),
  getPlan: () => requestAllowingMissing("/plan"),
  completeTask: (taskId) => request(`/tasks/${taskId}/complete`, { method: "POST" }),
  ignoreTask: (taskId) => request(`/tasks/${taskId}/ignore`, { method: "POST" }),
  getCareerHealth: () => request("/career-health"),
  getExplanation: () => request("/explain"),
};
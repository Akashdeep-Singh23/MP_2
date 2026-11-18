const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

export async function fetchWithAuth(endpoint, options = {}, token = null) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const errorMsg = data?.error?.message || `HTTP error ${response.status}`;
    const errorObj = new Error(errorMsg);
    errorObj.status = response.status;
    errorObj.code = data?.error?.code;
    errorObj.details = data?.error?.details;
    throw errorObj;
  }

  return data;
}

export const api = {
  getHealth: () => fetchWithAuth("/health"),
  getProfile: (token) => fetchWithAuth("/profile", { method: "GET" }, token),
  updateProfile: (profileData, token) => fetchWithAuth("/profile", { method: "PUT", body: JSON.stringify(profileData) }, token),
  getRecommendations: (token) => fetchWithAuth("/recommendations", { method: "POST" }, token),
  getHistory: (token) => fetchWithAuth("/history", { method: "GET" }, token),
  logCompletion: (workoutId, idempotencyKey, token) => fetchWithAuth("/history", {
    method: "POST",
    body: JSON.stringify({ workout_id: workoutId, idempotency_key: idempotencyKey })
  }, token),
  getDashboard: (token) => fetchWithAuth("/dashboard", { method: "GET" }, token),
  getNutrition: () => fetchWithAuth("/nutrition", { method: "GET" }),
  deleteAccount: (confirmation, token) => fetchWithAuth("/account", {
    method: "DELETE",
    body: JSON.stringify({ confirmation })
  }, token)
};

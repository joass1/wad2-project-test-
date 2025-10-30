import { auth } from "@/lib/firebase";

// Support both Vite (import.meta.env) and Vue CLI (process.env.VUE_APP_API_URL)
const API_BASE_URL = (import.meta?.env?.VITE_API_URL || process.env?.VUE_APP_API_URL || "http://localhost:8000");

async function authorizedFetch(path, options = {}) {
  const user = auth.currentUser;
  const token = user ? await user.getIdToken() : null;

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers ?? {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  const base = API_BASE_URL.replace(/\/$/, "");
  const response = await fetch(`${base}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    const message = detail.detail ?? detail.message ?? response.statusText;

    throw new Error(message);
  }

  return response.json();
}

export const api = {
  get: (path) => authorizedFetch(path),
  post: (path, body) =>
    authorizedFetch(path, { method: "POST", body: JSON.stringify(body) }),
  patch: (path, body) =>
    authorizedFetch(path, { method: "PATCH", body: JSON.stringify(body) }),
  put: (path, body) =>
    authorizedFetch(path, { method: "PUT", body: JSON.stringify(body) }),
  del: (path) => authorizedFetch(path, { method: "DELETE" }),
};

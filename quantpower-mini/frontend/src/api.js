export const API_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
export const WS_URL = (import.meta.env.VITE_WS_URL || API_URL.replace(/^http/, "ws")).replace(/\/$/, "");

const ACCESS = "qp_access";
const REFRESH = "qp_refresh";

export const auth = {
  get access() { return localStorage.getItem(ACCESS); },
  get refresh() { return localStorage.getItem(REFRESH); },
  set(access, refresh) {
    localStorage.setItem(ACCESS, access);
    if (refresh) localStorage.setItem(REFRESH, refresh);
  },
  clear() {
    localStorage.removeItem(ACCESS);
    localStorage.removeItem(REFRESH);
  },
};

export async function login(username, password) {
  const res = await fetch(`${API_URL}/api/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Login failed");
  auth.set(data.access, data.refresh);
}

async function refreshAccess() {
  if (!auth.refresh) return false;
  const res = await fetch(`${API_URL}/api/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: auth.refresh }),
  });
  if (!res.ok) return false;
  const data = await res.json();
  auth.set(data.access, data.refresh);
  return true;
}

export async function api(path, { method = "GET", body } = {}, retry = true) {
  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(auth.access ? { Authorization: `Bearer ${auth.access}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401 && retry && (await refreshAccess())) {
    return api(path, { method, body }, false);
  }
  if (res.status === 401) {
    auth.clear();
    window.location.href = "/login";
    throw new Error("Session expired");
  }

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const err = new Error(data?.error || data?.message || data?.detail || `HTTP ${res.status}`);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

// DRF list endpoints may or may not be paginated
export const asList = (d) => (Array.isArray(d) ? d : d?.results || []);

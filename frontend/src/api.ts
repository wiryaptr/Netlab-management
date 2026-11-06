const API = "/api/v1";

let csrfToken: string | null = null;

export async function csrf(): Promise<string> {
  if (csrfToken) return csrfToken;
  const res = await fetch(`${API}/auth/csrf/`, { credentials: "include" });
  const data = await res.json();
  csrfToken = data.csrf_token || "";
  return csrfToken!;
}

function headers(json = true): Record<string, string> {
  const h: Record<string, string> = json ? { "Content-Type": "application/json" } : {};
  if (csrfToken) h["X-CSRFToken"] = csrfToken;
  return h;
}

export async function api<T>(
  path: string,
  opts: { method?: string; body?: unknown; params?: Record<string, string | number | undefined> } = {}
): Promise<T> {
  await csrf();
  const { method = "GET", body, params } = opts;
  let url = `${API}${path}`;
  if (params) {
    const q = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined) as [string, string][]
    ).toString();
    if (q) url += `?${q}`;
  }
  const res = await fetch(url, {
    method,
    credentials: "include",
    headers: headers(!!body),
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
  });
  if (res.status === 204) return undefined as T;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = (data as { error?: { message?: string } }).error;
    throw new Error(err?.message || `HTTP ${res.status}`);
  }
  return data as T;
}

export async function uploadCsvImport(
  file: File,
  resource: string,
  mode: "preview" | "commit"
): Promise<unknown> {
  await csrf();
  const form = new FormData();
  form.append("file", file);
  form.append("resource", resource);
  form.append("mode", mode);
  const res = await fetch(`${API}/imports/`, {
    method: "POST",
    credentials: "include",
    headers: headers(false),
    body: form,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = (data as { error?: { message?: string } }).error;
    throw new Error(err?.message || `HTTP ${res.status}`);
  }
  return data;
}

export interface Me {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  permissions: string[];
}

export function login(username: string, password: string): Promise<{ user: Me }> {
  return api("/auth/login/", { method: "POST", body: { username, password } });
}

export function logout(): Promise<void> {
  return api<void>("/auth/logout/", { method: "POST" });
}

export function me(): Promise<Me> {
  return api(`/auth/me/`);
}

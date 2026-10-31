/**
 * Core HTTP client for the Neer Niti backend.
 *
 * Uses the native fetch API.
 *
 * Base URL resolution:
 *   - In development, the default relative base `/api/v1` is proxied to
 *     http://localhost:8000 by Vite (see vite.config.js).
 *   - For other deployments, set VITE_API_BASE_URL (e.g.
 *     "https://api.example.com") — the client appends `/api/v1` to it.
 *     No secrets are placed here; this is a public base URL only.
 *
 * All backend error responses follow the shape:
 *   { "error": "CODE", "message": "...", "details"?: [...] }
 */

const ENV_BASE = import.meta.env?.VITE_API_BASE_URL?.replace(/\/+$/, '') || ''
const BASE = `${ENV_BASE}/api/v1`
const HEALTH_PATH = `${ENV_BASE}/health`

export class ApiError extends Error {
  constructor(message, { status, code, details } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }

  /** True for authentication/authorization failures (e.g. missing/invalid admin key). */
  get isAuthError() {
    return this.status === 401 || this.status === 403
  }

  /** True when the requested resource was not found. */
  get isNotFound() {
    return this.status === 404
  }

  /** True when the backend was unreachable. */
  get isNetworkError() {
    return this.status === 0
  }
}

async function parseBody(res) {
  const text = await res.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    return text
  }
}

async function request(path, { method = 'GET', body, headers = {}, raw = false } = {}) {
  const opts = {
    method,
    headers: { ...headers },
  }

  if (body !== undefined && !(body instanceof FormData)) {
    opts.headers['Content-Type'] = 'application/json'
    opts.body = JSON.stringify(body)
  } else if (body instanceof FormData) {
    opts.body = body
  }

  let res
  try {
    res = await fetch(raw ? path : `${BASE}${path}`, opts)
  } catch {
    throw new ApiError(
      'Could not reach the server. Please check that the backend is running.',
      { status: 0, code: 'NETWORK_ERROR' },
    )
  }

  const data = await parseBody(res)

  if (!res.ok) {
    const message =
      (data && typeof data === 'object' && data.message) ||
      `Request failed with status ${res.status}`
    throw new ApiError(message, {
      status: res.status,
      code: (data && data.error) || 'HTTP_ERROR',
      details: (data && data.details) || null,
    })
  }

  return data
}

export const http = {
  get: (path, opts) => request(path, { ...opts, method: 'GET' }),
  post: (path, body, opts) => request(path, { ...opts, method: 'POST', body }),
  patch: (path, body, opts) => request(path, { ...opts, method: 'PATCH', body }),
  del: (path, opts) => request(path, { ...opts, method: 'DELETE' }),
  // Health is not under /api/v1
  health: () => request(HEALTH_PATH, { raw: true }),
}

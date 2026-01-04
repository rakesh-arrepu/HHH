/**
 * Determine API root:
 * - Prefer VITE_API_URL when provided at build time
 * - If hosted on GitHub Pages and VITE_API_URL is not set, default to Render backend
 * - In local dev (no VITE_API_URL and not on GitHub Pages), fallback to '/api' (Vite proxy/dev)
 */
function inferDefaultApi(): string {
  if (typeof window !== 'undefined') {
    const host = window.location.hostname
    if (host.endsWith('github.io')) {
      return 'https://hhh-backend.onrender.com'
    }
  }
  return ''
}

const explicitRoot = (import.meta.env.VITE_API_URL ?? '').toString().trim()
const inferredRoot = inferDefaultApi()
const API_ROOT = explicitRoot || inferredRoot
const API_BASE = API_ROOT ? `${API_ROOT.replace(/\/$/, '')}/api` : '/api'

/**
 * Custom API error class that preserves HTTP status code and error details
 */
export class ApiError extends Error {
  status: number
  code?: string
  detail: string

  constructor(status: number, detail: string, code?: string) {
    super(detail)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
    this.code = code
  }

  /**
   * Check if this is an authentication error (401)
   */
  isAuthError(): boolean {
    return this.status === 401
  }

  /**
   * Check if this is a forbidden error (403)
   */
  isForbiddenError(): boolean {
    return this.status === 403
  }

  /**
   * Check if this is a not found error (404)
   */
  isNotFoundError(): boolean {
    return this.status === 404
  }

  /**
   * Check if this is a validation error (400/422)
   */
  isValidationError(): boolean {
    return this.status === 400 || this.status === 422
  }

  /**
   * Check if this is a server error (5xx)
   */
  isServerError(): boolean {
    return this.status >= 500
  }

  /**
   * Check if this is a network error
   */
  isNetworkError(): boolean {
    return this.status === 0
  }
}

type RequestOptions = {
  method?: string
  body?: unknown
}

// Event for auth state changes (session expired, etc.)
type AuthEventType = 'session_expired' | 'unauthorized'
type AuthEventCallback = (event: AuthEventType) => void
let authEventCallback: AuthEventCallback | null = null

/**
 * Register a callback for auth events (session expiry, etc.)
 */
export function onAuthEvent(callback: AuthEventCallback): () => void {
  authEventCallback = callback
  return () => {
    authEventCallback = null
  }
}

// ============== Token Storage ==============
const TOKEN_KEY = 'auth_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  // Add Authorization header if token exists
  const token = getToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const config: RequestInit = {
    method: options.method || 'GET',
    headers,
    credentials: 'include', // Keep for backward compatibility with local dev
  }

  if (options.body) {
    config.body = JSON.stringify(options.body)
  }

  let response: Response
  try {
    response = await fetch(`${API_BASE}${endpoint}`, config)
  } catch (err) {
    // Network error (no internet, CORS blocked, server unreachable)
    throw new ApiError(
      0,
      'Unable to connect to server. Please check your internet connection.',
      'NETWORK_ERROR'
    )
  }

  if (!response.ok) {
    let errorData: { detail?: string; code?: string } = { detail: 'An error occurred' }

    try {
      errorData = await response.json()
    } catch {
      // Response wasn't JSON, use status text
      errorData = { detail: response.statusText || 'Request failed' }
    }

    const detail = errorData.detail || 'Request failed'
    const code = errorData.code
    const apiError = new ApiError(response.status, detail, code)

    // Notify auth callback for 401 errors (but not for login/register endpoints)
    if (apiError.isAuthError() && authEventCallback) {
      const isAuthEndpoint = endpoint.startsWith('/auth/login') ||
                             endpoint.startsWith('/auth/register') ||
                             endpoint.startsWith('/auth/password')
      if (!isAuthEndpoint) {
        authEventCallback('session_expired')
      }
    }

    throw apiError
  }

  // Handle empty responses (204 No Content, etc.)
  const contentType = response.headers.get('content-type')
  if (!contentType || !contentType.includes('application/json')) {
    return {} as T
  }

  try {
    return await response.json()
  } catch {
    return {} as T
  }
}

// Auth
export const api = {
  // Auth
  register: async (data: { email: string; password: string; name: string }) => {
    const response = await request<{ id: number; email: string; name: string; token: string }>('/auth/register', { method: 'POST', body: data })
    // Store token for cross-origin auth
    if (response.token) {
      setToken(response.token)
    }
    return response
  },

  login: async (data: { email: string; password: string }) => {
    const response = await request<{ id: number; email: string; name: string; token: string }>('/auth/login', { method: 'POST', body: data })
    // Store token for cross-origin auth
    if (response.token) {
      setToken(response.token)
    }
    return response
  },

  logout: () => {
    clearToken() // Clear token from localStorage
    return request<{ message: string }>('/auth/logout', { method: 'POST' })
  },

  getMe: () => request<{ id: number; email: string; name: string }>('/auth/me'),

  forgotPassword: (email: string) =>
    request<{
      message: string
      email_sent?: boolean
      reset_token?: string
      email_configured?: boolean
      email_error?: string
    }>('/auth/password/forgot', {
      method: 'POST',
      body: { email },
    }),

  resetPassword: (token: string, password: string) =>
    request<{ message: string }>('/auth/password/reset', {
      method: 'POST',
      body: { token, password },
    }),

  // Groups
  getGroups: () =>
    request<{ id: number; name: string; owner_id: number; is_owner: boolean }[]>('/groups'),

  createGroup: (name: string) =>
    request<{ id: number; name: string; owner_id: number; is_owner: boolean }>('/groups', {
      method: 'POST',
      body: { name },
    }),

  updateGroup: (groupId: number, name: string) =>
    request<{ id: number; name: string; owner_id: number; is_owner: boolean }>(`/groups/${groupId}`, {
      method: 'PUT',
      body: { name },
    }),

  getMembers: (groupId: number) =>
    request<{ id: number; user_id: number; name: string; email: string }[]>(`/groups/${groupId}/members`),

  addMember: (groupId: number, email: string) =>
    request<{ id: number; user_id: number; name: string; email: string }>(`/groups/${groupId}/members`, {
      method: 'POST',
      body: { email },
    }),

  removeMember: (groupId: number, userId: number) =>
    request<{ message: string }>(`/groups/${groupId}/members/${userId}`, { method: 'DELETE' }),

  transferOwnership: (groupId: number, newOwnerId: number) =>
    request<{ message: string; group: { id: number; name: string; owner_id: number; is_owner: boolean } }>(
      `/groups/${groupId}/owner`,
      {
        method: 'PUT',
        body: { new_owner_id: newOwnerId },
      }
    ),

  // Entries
  getEntries: (groupId: number, date?: string, userId?: number) => {
    const params = new URLSearchParams({ group_id: String(groupId) })
    if (date) params.append('entry_date', date)
    if (userId !== undefined) params.append('user_id', String(userId))
    return request<{
      id: number
      section: string
      content: string
      date: string
      user_id: number
      user_name: string
    }[]>(`/entries?${params}`)
  },

  createEntry: (data: { group_id: number; section: string; content: string; entry_date?: string }) =>
    request<{
      id: number
      section: string
      content: string
      date: string
      user_id: number
      user_name: string
    }>('/entries', { method: 'POST', body: data }),

  // Analytics
  getStreak: (groupId: number, userId?: number) => {
    const params = new URLSearchParams({ group_id: String(groupId) })
    if (userId !== undefined) params.append('user_id', String(userId))
    return request<{ streak: number; last_complete_date: string | null }>(`/analytics/streak?${params}`)
  },

  getHistory: (groupId: number, days = 30, userId?: number) => {
    const params = new URLSearchParams({
      group_id: String(groupId),
      days: String(days)
    })
    if (userId !== undefined) params.append('user_id', String(userId))
    return request<{ date: string; completed_sections: string[]; is_complete: boolean }[]>(
      `/analytics/history?${params}`
    )
  },
}

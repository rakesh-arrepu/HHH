const API_ROOT = (import.meta.env.VITE_API_URL ?? '').toString().trim()
const API_BASE = API_ROOT ? `${API_ROOT.replace(/\/$/, '')}/api` : '/api'

type RequestOptions = {
  method?: string
  body?: unknown
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const config: RequestInit = {
    method: options.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
  }

  if (options.body) {
    config.body = JSON.stringify(options.body)
  }

  const response = await fetch(`${API_BASE}${endpoint}`, config)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }))
    throw new Error(error.detail || 'Request failed')
  }

  return response.json()
}

// Auth
export const api = {
  // Auth
  register: (data: { email: string; password: string; name: string }) =>
    request<{ id: number; email: string; name: string }>('/auth/register', { method: 'POST', body: data }),

  login: (data: { email: string; password: string }) =>
    request<{ id: number; email: string; name: string }>('/auth/login', { method: 'POST', body: data }),

  logout: () => request<{ message: string }>('/auth/logout', { method: 'POST' }),

  getMe: () => request<{ id: number; email: string; name: string }>('/auth/me'),

  // Groups
  getGroups: () =>
    request<{ id: number; name: string; owner_id: number; is_owner: boolean }[]>('/groups'),

  createGroup: (name: string) =>
    request<{ id: number; name: string; owner_id: number; is_owner: boolean }>('/groups', {
      method: 'POST',
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

  // Entries
  getEntries: (groupId: number, date?: string) => {
    const params = new URLSearchParams({ group_id: String(groupId) })
    if (date) params.append('entry_date', date)
    return request<{
      id: number
      section: string
      content: string
      date: string
      user_id: number
      user_name: string
    }[]>(`/entries?${params}`)
  },

  createEntry: (data: { group_id: number; section: string; content: string; date?: string }) =>
    request<{
      id: number
      section: string
      content: string
      date: string
      user_id: number
      user_name: string
    }>('/entries', { method: 'POST', body: data }),

  // Analytics
  getStreak: (groupId: number) =>
    request<{ streak: number; last_complete_date: string | null }>(`/analytics/streak?group_id=${groupId}`),

  getHistory: (groupId: number, days = 30) =>
    request<{ date: string; completed_sections: string[]; is_complete: boolean }[]>(
      `/analytics/history?group_id=${groupId}&days=${days}`
    ),
}

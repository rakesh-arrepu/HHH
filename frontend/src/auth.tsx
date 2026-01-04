import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import { api, onAuthEvent, ApiError } from './api'

type User = {
  id: number
  email: string
  name: string
} | null

type AuthContextType = {
  user: User
  loading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  logout: () => Promise<void>
  clearError: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const clearError = useCallback(() => setError(null), [])

  const handleLogout = useCallback(async () => {
    try {
      await api.logout()
    } catch {
      // Ignore logout errors, clear user anyway
    }
    setUser(null)
    setError(null)
  }, [])

  const refreshUser = useCallback(async () => {
    try {
      const userData = await api.getMe()
      setUser(userData)
      setError(null)
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.isAuthError()) {
          // Session expired or invalid
          setUser(null)
          setError('Your session has expired. Please log in again.')
        } else if (err.isNetworkError()) {
          setError('Unable to connect to server. Please check your internet connection.')
        } else {
          setError(err.detail)
        }
      } else {
        setUser(null)
      }
    }
  }, [])

  useEffect(() => {
    // Check if already logged in
    const checkAuth = async () => {
      try {
        const userData = await api.getMe()
        setUser(userData)
      } catch (err) {
        if (err instanceof ApiError && err.isAuthError()) {
          // Not logged in - this is normal, not an error
          setUser(null)
        } else if (err instanceof ApiError && err.isNetworkError()) {
          setError('Unable to connect to server. Please check your internet connection.')
        }
        // For other errors, just set user to null
        setUser(null)
      } finally {
        setLoading(false)
      }
    }
    checkAuth()
  }, [])

  // Listen for auth events (session expiry from API calls)
  useEffect(() => {
    const unsubscribe = onAuthEvent((event) => {
      if (event === 'session_expired') {
        setUser(null)
        setError('Your session has expired. Please log in again.')
      }
    })
    return unsubscribe
  }, [])

  const login = async (email: string, password: string) => {
    setError(null)
    try {
      const userData = await api.login({ email, password })
      setUser(userData)
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.isAuthError()) {
          throw new Error('Invalid email or password')
        } else if (err.isNetworkError()) {
          throw new Error('Unable to connect to server. Please try again.')
        } else {
          throw new Error(err.detail)
        }
      }
      throw err
    }
  }

  const register = async (email: string, password: string, name: string) => {
    setError(null)
    try {
      const userData = await api.register({ email, password, name })
      setUser(userData)
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.isValidationError()) {
          throw new Error(err.detail || 'Please check your input and try again.')
        } else if (err.isNetworkError()) {
          throw new Error('Unable to connect to server. Please try again.')
        } else {
          throw new Error(err.detail)
        }
      }
      throw err
    }
  }

  const logout = async () => {
    await handleLogout()
  }

  return (
    <AuthContext.Provider value={{ user, loading, error, login, register, logout, clearError, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

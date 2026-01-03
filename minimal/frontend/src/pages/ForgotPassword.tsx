import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [info, setInfo] = useState<string | null>(null)
  const [devToken, setDevToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setInfo(null)
    setDevToken(null)
    setLoading(true)

    try {
      const res = await api.forgotPassword(email)
      setInfo('If an account exists for this email, a reset link has been sent.')
      // For local/dev, backend returns reset_token for convenience
      if (res.reset_token) {
        setDevToken(res.reset_token)
      }
    } catch (err) {
      // Still show generic success to avoid user enumeration
      setInfo('If an account exists for this email, a reset link has been sent.')
    } finally {
      setLoading(false)
    }
  }

  const goToReset = () => {
    if (devToken) {
      navigate(`/reset-password?token=${encodeURIComponent(devToken)}`)
    }
  }

  return (
    <div className="max-w-md mx-auto mt-16">
      <h1 className="text-2xl font-bold text-center mb-8">Forgot Password</h1>

      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow-sm border">
        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md text-sm">
            {error}
          </div>
        )}
        {info && (
          <div className="mb-4 p-3 bg-green-50 text-green-700 rounded-md text-sm">
            {info}
          </div>
        )}

        <div className="mb-4">
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2 px-4 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? 'Submitting...' : 'Send reset link'}
        </button>

        <p className="mt-4 text-center text-sm text-gray-600">
          Remembered your password?{' '}
          <Link to="/login" className="text-indigo-600 hover:underline">
            Back to Login
          </Link>
        </p>

        {devToken && (
          <div className="mt-6 p-3 border rounded-md bg-gray-50">
            <div className="text-xs text-gray-600 mb-2">
              Development token (not shown in production):
            </div>
            <code className="block text-xs break-all mb-2">{devToken}</code>
            <button
              type="button"
              onClick={goToReset}
              className="w-full py-2 px-4 bg-gray-800 text-white rounded-md hover:bg-gray-900"
            >
              Continue to Reset Password
            </button>
          </div>
        )}
      </form>
    </div>
  )
}

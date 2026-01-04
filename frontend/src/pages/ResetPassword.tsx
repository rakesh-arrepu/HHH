import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { api } from '../api'
import { motion } from 'framer-motion'
import {
  Lock,
  KeyRound,
  ArrowLeft,
  ShieldCheck,
  CheckCircle,
  AlertTriangle,
  Eye,
  EyeOff
} from 'lucide-react'
import { GlassCard, GlowButton, InputField } from '../components/ui'
import { celebrateSuccess } from '../components/ui/confetti'

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const [token, setToken] = useState<string | null>(null)
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const t = searchParams.get('token')
    setToken(t)
  }, [searchParams])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setInfo(null)

    if (!token) {
      setError('Missing reset token. Please use the link from your email.')
      return
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters.')
      return
    }
    if (password !== confirm) {
      setError('Passwords do not match.')
      return
    }

    setLoading(true)
    try {
      await api.resetPassword(token, password)
      setInfo('Password has been reset successfully. Redirecting to login...')
      celebrateSuccess()
      setTimeout(() => navigate('/login'), 2000)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Reset failed. Try again.'
      // Check for common error patterns
      if (message.toLowerCase().includes('expired') || message.toLowerCase().includes('invalid')) {
        setError('This reset link has expired or is invalid. Please request a new password reset.')
        setToken(null) // Clear invalid token
      } else {
        setError(message)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', bounce: 0.5, delay: 0.2 }}
            className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 flex items-center justify-center shadow-2xl"
            style={{ boxShadow: '0 0 60px rgba(16, 185, 129, 0.4)' }}
          >
            <ShieldCheck className="w-10 h-10 text-white" />
          </motion.div>
          <h1 className="text-3xl font-bold text-white mb-2">Reset Password</h1>
          <p className="text-white/60">Create a new secure password</p>
        </motion.div>

        {/* Form */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <GlassCard className="p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-start gap-3"
                >
                  <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <p className="text-red-400 text-sm">{error}</p>
                </motion.div>
              )}

              {info && (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-start gap-3"
                >
                  <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <p className="text-emerald-400 text-sm">{info}</p>
                </motion.div>
              )}

              {!token && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30"
                >
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-amber-400 text-sm mb-2">
                        Missing or invalid token.
                      </p>
                      <Link
                        to="/forgot-password"
                        className="text-purple-400 hover:text-purple-300 text-sm underline"
                      >
                        Request a new reset link
                      </Link>
                    </div>
                  </div>
                </motion.div>
              )}

              <div className="relative">
                <InputField
                  type={showPassword ? 'text' : 'password'}
                  label="New Password"
                  icon={Lock}
                  placeholder="Enter new password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-[38px] text-white/40 hover:text-white/60 transition-colors"
                >
                  {showPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>

              <InputField
                type={showPassword ? 'text' : 'password'}
                label="Confirm Password"
                icon={KeyRound}
                placeholder="Confirm new password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                required
                minLength={6}
              />

              <p className="text-xs text-white/40">
                Password must be at least 6 characters
              </p>

              <GlowButton
                type="submit"
                loading={loading}
                icon={ShieldCheck}
                fullWidth
                size="lg"
                variant="success"
                disabled={!token}
              >
                {loading ? 'Resetting...' : 'Reset Password'}
              </GlowButton>

              <Link
                to="/login"
                className="flex items-center justify-center gap-2 w-full py-3 rounded-xl border border-white/20 text-white/80 hover:text-white hover:bg-white/5 hover:border-white/30 transition-all duration-300"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to Login</span>
              </Link>
            </form>
          </GlassCard>
        </motion.div>
      </div>
    </div>
  )
}

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { motion } from 'framer-motion'
import {
  Mail,
  KeyRound,
  ArrowLeft,
  Send,
  AlertTriangle,
  Inbox,
  RefreshCw
} from 'lucide-react'
import { GlassCard, GlowButton, InputField } from '../components/ui'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [emailSent, setEmailSent] = useState(false)
  const [devToken, setDevToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess(false)
    setEmailSent(false)
    setDevToken(null)
    setLoading(true)

    try {
      const res = await api.forgotPassword(email)
      setSuccess(true)

      // Check if email was actually sent
      if (res.email_sent) {
        setEmailSent(true)
      }

      // Dev mode fallback: show token if email not configured
      if (res.reset_token) {
        setDevToken(res.reset_token)
      }
    } catch {
      // Still show success to avoid user enumeration
      setSuccess(true)
    } finally {
      setLoading(false)
    }
  }

  const goToReset = () => {
    if (devToken) {
      navigate(`/reset-password?token=${encodeURIComponent(devToken)}`)
    }
  }

  const handleTryAgain = () => {
    setSuccess(false)
    setEmailSent(false)
    setDevToken(null)
    setError('')
  }

  // Success state - show check your email message
  if (success && !devToken) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <GlassCard className="p-8 text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', bounce: 0.5, delay: 0.2 }}
                className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-2xl"
                style={{ boxShadow: '0 0 60px rgba(16, 185, 129, 0.4)' }}
              >
                <Inbox className="w-10 h-10 text-white" />
              </motion.div>

              <h2 className="text-2xl font-bold text-white mb-3">Check Your Email</h2>

              <p className="text-white/70 mb-6">
                {emailSent
                  ? `We've sent a password reset link to ${email}. The link will expire in 15 minutes.`
                  : `If an account exists for ${email}, you will receive a password reset link shortly.`}
              </p>

              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                  <p className="text-white/50 text-sm">
                    Didn't receive the email? Check your spam folder or try again.
                  </p>
                </div>

                <button
                  onClick={handleTryAgain}
                  className="flex items-center justify-center gap-2 w-full py-3 rounded-xl text-white/70 hover:text-white hover:bg-white/5 transition-all duration-300"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Try a different email</span>
                </button>

                <Link
                  to="/login"
                  className="flex items-center justify-center gap-2 w-full py-3 rounded-xl border border-white/20 text-white/80 hover:text-white hover:bg-white/5 hover:border-white/30 transition-all duration-300"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Back to Login</span>
                </Link>
              </div>
            </GlassCard>
          </motion.div>
        </div>
      </div>
    )
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
            className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-500 flex items-center justify-center shadow-2xl"
            style={{ boxShadow: '0 0 60px rgba(99, 102, 241, 0.4)' }}
          >
            <KeyRound className="w-10 h-10 text-white" />
          </motion.div>
          <h1 className="text-3xl font-bold text-white mb-2">Forgot Password?</h1>
          <p className="text-white/60">No worries, we'll send you reset instructions</p>
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

              <InputField
                type="email"
                label="Email Address"
                icon={Mail}
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />

              <GlowButton
                type="submit"
                loading={loading}
                icon={Send}
                fullWidth
                size="lg"
              >
                {loading ? 'Sending...' : 'Send Reset Link'}
              </GlowButton>

              <Link
                to="/login"
                className="flex items-center justify-center gap-2 w-full py-3 rounded-xl border border-white/20 text-white/80 hover:text-white hover:bg-white/5 hover:border-white/30 transition-all duration-300"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to Login</span>
              </Link>

              {/* Dev token section - only shows when email is not configured */}
              {devToken && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-6 p-4 rounded-xl bg-amber-500/10 border border-amber-500/30"
                >
                  <div className="flex items-center gap-2 text-amber-400 text-sm mb-3">
                    <AlertTriangle className="w-4 h-4" />
                    <span className="font-medium">Development Mode</span>
                  </div>
                  <p className="text-white/50 text-xs mb-3">
                    Email service not configured. Use this token to reset your password:
                  </p>
                  <code className="block text-xs text-white/60 break-all mb-4 bg-black/20 p-2 rounded">
                    {devToken}
                  </code>
                  <GlowButton
                    type="button"
                    onClick={goToReset}
                    fullWidth
                    variant="secondary"
                  >
                    Continue to Reset Password
                  </GlowButton>
                </motion.div>
              )}
            </form>
          </GlassCard>
        </motion.div>
      </div>
    </div>
  )
}

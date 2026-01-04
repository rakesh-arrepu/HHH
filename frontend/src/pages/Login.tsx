import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import { motion } from 'framer-motion'
import {
  Mail,
  Lock,
  LogIn,
  Sparkles,
  Heart,
  Smile,
  Coins,
  ArrowRight
} from 'lucide-react'
import { GlassCard, GlowButton, InputField } from '../components/ui'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(email, password)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const features = [
    { icon: Heart, label: 'Health', color: 'from-emerald-400 to-teal-500', glow: 'shadow-emerald-500/30' },
    { icon: Smile, label: 'Happiness', color: 'from-amber-400 to-orange-500', glow: 'shadow-amber-500/30' },
    { icon: Coins, label: 'Hela', color: 'from-yellow-400 to-amber-500', glow: 'shadow-yellow-500/30' },
  ]

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo & Title */}
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
            className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-purple-500 via-pink-500 to-orange-400 flex items-center justify-center shadow-2xl"
            style={{ boxShadow: '0 0 60px rgba(139, 92, 246, 0.4)' }}
          >
            <Sparkles className="w-10 h-10 text-white" />
          </motion.div>
          <h1 className="text-3xl font-bold text-white mb-2">Welcome Back</h1>
          <p className="text-white/60">Track your daily HHH journey</p>
        </motion.div>

        {/* Feature Pills */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex justify-center gap-3 mb-8"
        >
          {features.map((feature, index) => (
            <motion.div
              key={feature.label}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4 + index * 0.1, type: 'spring' }}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-r ${feature.color} shadow-lg ${feature.glow}`}
            >
              <feature.icon className="w-4 h-4 text-white" />
              <span className="text-xs font-semibold text-white">{feature.label}</span>
            </motion.div>
          ))}
        </motion.div>

        {/* Login Form */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <GlassCard className="p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="p-4 rounded-xl bg-red-500/10 border border-red-500/30"
                >
                  <p className="text-red-400 text-sm">{error}</p>
                </motion.div>
              )}

              <InputField
                type="email"
                label="Email"
                icon={Mail}
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />

              <InputField
                type="password"
                label="Password"
                icon={Lock}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />

              <div className="flex justify-end">
                <Link
                  to="/forgot-password"
                  className="text-sm text-purple-400 hover:text-purple-300 transition-colors"
                >
                  Forgot password?
                </Link>
              </div>

              <GlowButton
                type="submit"
                loading={loading}
                icon={LogIn}
                fullWidth
                size="lg"
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </GlowButton>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-white/10" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-transparent text-white/40">New here?</span>
                </div>
              </div>

              <Link
                to="/register"
                className="flex items-center justify-center gap-2 w-full py-3 rounded-xl border border-white/20 text-white/80 hover:text-white hover:bg-white/5 hover:border-white/30 transition-all duration-300"
              >
                <span>Create an account</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </form>
          </GlassCard>
        </motion.div>

        {/* Footer */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="text-center text-white/30 text-sm mt-8"
        >
          Track your Health, Happiness & Hela daily
        </motion.p>
      </div>
    </div>
  )
}

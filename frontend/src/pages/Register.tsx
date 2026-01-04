import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import { motion } from 'framer-motion'
import {
  User,
  Mail,
  Lock,
  UserPlus,
  Sparkles,
  Check,
  ArrowLeft
} from 'lucide-react'
import { GlassCard, GlowButton, InputField } from '../components/ui'
import { celebrateSuccess } from '../components/ui/confetti'

export default function Register() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await register(email, password, name)
      celebrateSuccess()
      setTimeout(() => navigate('/'), 500)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const benefits = [
    'Track your daily wellness',
    'Join groups with friends',
    'Build streaks & habits',
    'Celebrate achievements',
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
            className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 flex items-center justify-center shadow-2xl"
            style={{ boxShadow: '0 0 60px rgba(16, 185, 129, 0.4)' }}
          >
            <Sparkles className="w-10 h-10 text-white" />
          </motion.div>
          <h1 className="text-3xl font-bold text-white mb-2">Join the Journey</h1>
          <p className="text-white/60">Start tracking your HHH today</p>
        </motion.div>

        {/* Benefits */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mb-8"
        >
          <div className="grid grid-cols-2 gap-2">
            {benefits.map((benefit, index) => (
              <motion.div
                key={benefit}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + index * 0.1 }}
                className="flex items-center gap-2 text-sm text-white/60"
              >
                <div className="w-5 h-5 rounded-full bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                  <Check className="w-3 h-3 text-emerald-400" />
                </div>
                <span>{benefit}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Register Form */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <GlassCard className="p-8">
            <form onSubmit={handleSubmit} className="space-y-5">
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
                type="text"
                label="Your Name"
                icon={User}
                placeholder="What should we call you?"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />

              <InputField
                type="email"
                label="Email"
                icon={Mail}
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />

              <div>
                <InputField
                  type="password"
                  label="Password"
                  icon={Lock}
                  placeholder="Create a password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                />
                <p className="mt-2 text-xs text-white/40">
                  At least 6 characters
                </p>
              </div>

              <GlowButton
                type="submit"
                loading={loading}
                icon={UserPlus}
                fullWidth
                size="lg"
                variant="success"
              >
                {loading ? 'Creating account...' : 'Create Account'}
              </GlowButton>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-white/10" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-transparent text-white/40">Already a member?</span>
                </div>
              </div>

              <Link
                to="/login"
                className="flex items-center justify-center gap-2 w-full py-3 rounded-xl border border-white/20 text-white/80 hover:text-white hover:bg-white/5 hover:border-white/30 transition-all duration-300"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to login</span>
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
          By registering, you agree to track your HHH honestly
        </motion.p>
      </div>
    </div>
  )
}

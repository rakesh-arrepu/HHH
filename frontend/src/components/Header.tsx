import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../auth'
import { motion } from 'framer-motion'
import {
  BookOpen,
  CalendarDays,
  Users,
  BarChart3,
  LogOut,
  Sparkles,
  User
} from 'lucide-react'

export default function Header() {
  const { user, logout } = useAuth()
  const location = useLocation()

  const links = [
    { to: '/', label: 'Journal', icon: BookOpen },
    { to: '/history', label: 'History', icon: CalendarDays },
    { to: '/analytics', label: 'Analytics', icon: BarChart3 },
    { to: '/groups', label: 'Groups', icon: Users },
  ]

  return (
    <motion.header
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="glass-card sticky top-0 z-50 border-x-0 border-t-0 rounded-none"
    >
      <div className="max-w-6xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link
            to="/"
            className="flex items-center gap-2 group"
          >
            <motion.div
              whileHover={{ rotate: 180, scale: 1.1 }}
              transition={{ duration: 0.3 }}
              className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 via-pink-500 to-orange-400 flex items-center justify-center shadow-lg"
              style={{ boxShadow: '0 0 20px rgba(139, 92, 246, 0.4)' }}
            >
              <Sparkles className="w-5 h-5 text-white" />
            </motion.div>
            <div className="hidden sm:block">
              <h1 className="text-lg font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-orange-400 bg-clip-text text-transparent">
                HHH Tracker
              </h1>
              <p className="text-[10px] text-white/50 -mt-1">Health • Happiness • Hela</p>
            </div>
          </Link>

          {/* Navigation - Desktop */}
          <nav className="hidden md:flex items-center gap-1">
            {links.map((link) => {
              const isActive = location.pathname === link.to
              const Icon = link.icon

              return (
                <Link
                  key={link.to}
                  to={link.to}
                  className="relative px-4 py-2 rounded-xl transition-all duration-300"
                >
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute inset-0 bg-white/10 rounded-xl"
                      style={{ boxShadow: '0 0 20px rgba(139, 92, 246, 0.3)' }}
                      transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                    />
                  )}
                  <span className={`relative flex items-center gap-2 text-sm font-medium transition-colors ${
                    isActive
                      ? 'text-white'
                      : 'text-white/60 hover:text-white'
                  }`}>
                    <Icon className="w-4 h-4" />
                    {link.label}
                  </span>
                </Link>
              )
            })}
          </nav>

          {/* User Section */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
              <div className="w-6 h-6 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <User className="w-3 h-3 text-white" />
              </div>
              <span className="text-sm text-white/80 font-medium">{user?.name}</span>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={logout}
              className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/5 border border-white/10
                         text-white/60 hover:text-white hover:bg-white/10 hover:border-white/20
                         transition-all duration-300"
            >
              <LogOut className="w-4 h-4" />
              <span className="text-sm font-medium hidden sm:inline">Logout</span>
            </motion.button>
          </div>
        </div>

        {/* Navigation - Mobile */}
        <nav className="flex md:hidden items-center justify-center gap-1 mt-3 pt-3 border-t border-white/10">
          {links.map((link) => {
            const isActive = location.pathname === link.to
            const Icon = link.icon

            return (
              <Link
                key={link.to}
                to={link.to}
                className={`relative flex-1 flex flex-col items-center gap-1 py-2 rounded-xl transition-all duration-300 ${
                  isActive
                    ? 'bg-white/10 text-white'
                    : 'text-white/50 hover:text-white hover:bg-white/5'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="text-xs font-medium">{link.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="mobileActiveTab"
                    className="absolute -bottom-0.5 left-1/2 -translate-x-1/2 w-8 h-1 rounded-full bg-gradient-to-r from-purple-500 to-pink-500"
                  />
                )}
              </Link>
            )
          })}
        </nav>
      </div>
    </motion.header>
  )
}

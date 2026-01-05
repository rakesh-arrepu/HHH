import { motion } from 'framer-motion'
import { Settings, Zap } from 'lucide-react'
import { ActivityIcon, getColorClasses } from './ActivityIcon'

interface Favorite {
  id: number
  activity_type: {
    id: number
    name: string
    icon: string
    color: string
    default_duration: number
  }
  display_order: number
}

interface QuickLogBarProps {
  favorites: Favorite[]
  onQuickLog: (activityTypeId: number) => void
  onManageFavorites: () => void
  loading?: boolean
  disabled?: boolean
}

export function QuickLogBar({
  favorites,
  onQuickLog,
  onManageFavorites,
  loading = false,
  disabled = false
}: QuickLogBarProps) {
  return (
    <div className="mb-4">
      <div className="flex items-center gap-2 mb-2">
        <Zap className="w-4 h-4 text-emerald-400" />
        <span className="text-xs font-medium text-white/50 uppercase tracking-wider">Quick Log</span>
      </div>

      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
        {/* Favorite Activity Buttons */}
        {favorites.map((fav, index) => {
          const colorClasses = getColorClasses(fav.activity_type.color)
          return (
            <motion.button
              key={fav.id}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onQuickLog(fav.activity_type.id)}
              disabled={disabled || loading}
              className={`
                flex items-center gap-2 px-3 py-2 rounded-xl
                bg-white/5 border ${colorClasses.border}
                hover:bg-white/10 hover:border-opacity-50
                transition-all duration-200
                disabled:opacity-50 disabled:cursor-not-allowed
                whitespace-nowrap flex-shrink-0
              `}
            >
              <ActivityIcon
                icon={fav.activity_type.icon}
                color={fav.activity_type.color}
                size="sm"
                variant="ghost"
              />
              <div className="text-left">
                <span className="text-sm font-medium text-white">
                  {fav.activity_type.name}
                </span>
                <span className="text-xs text-white/40 block">
                  {fav.activity_type.default_duration}m
                </span>
              </div>
            </motion.button>
          )
        })}

        {/* Manage Favorites Button */}
        <motion.button
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: favorites.length * 0.05 }}
          whileHover={{ scale: 1.05, rotate: 90 }}
          whileTap={{ scale: 0.95 }}
          onClick={onManageFavorites}
          disabled={disabled}
          className={`
            p-2.5 rounded-xl
            bg-white/5 border border-white/10
            hover:bg-white/10 hover:border-white/20
            transition-all duration-200
            disabled:opacity-50 disabled:cursor-not-allowed
            flex-shrink-0
          `}
          title="Manage favorites"
        >
          <Settings className="w-4 h-4 text-white/50" />
        </motion.button>
      </div>
    </div>
  )
}

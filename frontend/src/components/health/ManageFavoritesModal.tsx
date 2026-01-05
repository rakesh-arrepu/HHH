import { useState, useMemo } from 'react'
import { createPortal } from 'react-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Search, Star, StarOff, Check } from 'lucide-react'
import { GlowButton } from '../ui'
import { ActivityIcon } from './ActivityIcon'
import { CATEGORY_LABELS } from '../../types/health'

interface ActivityType {
  id: number
  name: string
  category: string
  icon: string
  color: string
  met_value: number
  default_duration: number
}

interface ActivityTypeGrouped {
  category: string
  activities: ActivityType[]
}

interface Favorite {
  id: number
  activity_type: ActivityType
  display_order: number
}

interface ManageFavoritesModalProps {
  isOpen: boolean
  onClose: () => void
  activityTypes: ActivityTypeGrouped[]
  favorites: Favorite[]
  onAddFavorite: (activityTypeId: number) => Promise<void>
  onRemoveFavorite: (activityTypeId: number) => Promise<void>
  loading?: boolean
}

export function ManageFavoritesModal({
  isOpen,
  onClose,
  activityTypes,
  favorites,
  onAddFavorite,
  onRemoveFavorite,
  loading = false
}: ManageFavoritesModalProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [pendingAction, setPendingAction] = useState<number | null>(null)

  // Create a set of favorited activity type IDs for quick lookup
  const favoritedIds = useMemo(() => {
    return new Set(favorites.map(f => f.activity_type.id))
  }, [favorites])

  // Filter activities by search
  const filteredTypes = useMemo(() => {
    if (!searchQuery.trim()) return activityTypes

    const query = searchQuery.toLowerCase()
    return activityTypes
      .map(group => ({
        ...group,
        activities: group.activities.filter(a =>
          a.name.toLowerCase().includes(query)
        )
      }))
      .filter(group => group.activities.length > 0)
  }, [activityTypes, searchQuery])

  const handleToggleFavorite = async (activity: ActivityType) => {
    setPendingAction(activity.id)
    try {
      if (favoritedIds.has(activity.id)) {
        await onRemoveFavorite(activity.id)
      } else {
        await onAddFavorite(activity.id)
      }
    } finally {
      setPendingAction(null)
    }
  }

  if (!isOpen) return null

  const modalContent = (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        style={{ zIndex: 9999 }}
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          onClick={e => e.stopPropagation()}
          className="w-full max-w-md max-h-[85vh] overflow-hidden rounded-2xl bg-[#1a1a2e] border border-white/10 shadow-2xl"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-white/10">
            <div>
              <h2 className="text-lg font-semibold text-white">Manage Favorites</h2>
              <p className="text-sm text-white/50">
                {favorites.length} favorites selected
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg text-white/50 hover:text-white hover:bg-white/10 transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-4 overflow-y-auto max-h-[calc(85vh-140px)]">
            {/* Search */}
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
              <input
                type="text"
                placeholder="Search activities..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-emerald-500/50 transition-all"
              />
            </div>

            {/* Current Favorites */}
            {favorites.length > 0 && !searchQuery && (
              <div className="mb-4">
                <h3 className="text-sm font-medium text-white/60 mb-2 flex items-center gap-2">
                  <Star className="w-4 h-4 text-yellow-400" />
                  Current Favorites
                </h3>
                <div className="flex flex-wrap gap-2">
                  {favorites.map(fav => (
                    <motion.button
                      key={fav.id}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => handleToggleFavorite(fav.activity_type)}
                      disabled={pendingAction === fav.activity_type.id || loading}
                      className="flex items-center gap-2 px-3 py-2 rounded-xl bg-yellow-500/20 border border-yellow-500/30 hover:bg-yellow-500/30 transition-all disabled:opacity-50"
                    >
                      <ActivityIcon
                        icon={fav.activity_type.icon}
                        color={fav.activity_type.color}
                        size="sm"
                        variant="ghost"
                      />
                      <span className="text-sm text-white">{fav.activity_type.name}</span>
                      <X className="w-3.5 h-3.5 text-yellow-400/60" />
                    </motion.button>
                  ))}
                </div>
              </div>
            )}

            {/* All Activities */}
            <div className="space-y-4">
              {filteredTypes.map(group => (
                <div key={group.category}>
                  <h3 className="text-sm font-medium text-white/60 mb-2">
                    {CATEGORY_LABELS[group.category] || group.category}
                  </h3>
                  <div className="grid grid-cols-2 gap-2">
                    {group.activities.map(activity => {
                      const isFavorited = favoritedIds.has(activity.id)
                      const isPending = pendingAction === activity.id

                      return (
                        <motion.button
                          key={activity.id}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => handleToggleFavorite(activity)}
                          disabled={isPending || loading}
                          className={`
                            flex items-center gap-2 p-2 rounded-xl text-left
                            transition-all disabled:opacity-50
                            ${isFavorited
                              ? 'bg-yellow-500/20 border border-yellow-500/30'
                              : 'bg-white/5 border border-white/10 hover:bg-white/10'
                            }
                          `}
                        >
                          <ActivityIcon
                            icon={activity.icon}
                            color={activity.color}
                            size="sm"
                          />
                          <span className="text-sm text-white flex-1 truncate">
                            {activity.name}
                          </span>
                          {isPending ? (
                            <div className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                          ) : isFavorited ? (
                            <Check className="w-4 h-4 text-yellow-400" />
                          ) : (
                            <StarOff className="w-4 h-4 text-white/30" />
                          )}
                        </motion.button>
                      )
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-white/10">
            <GlowButton
              variant="primary"
              onClick={onClose}
              className="w-full"
            >
              Done
            </GlowButton>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )

  return createPortal(modalContent, document.body)
}

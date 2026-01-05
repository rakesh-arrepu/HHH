import { motion, AnimatePresence } from 'framer-motion'
import { Clock, Flame, MapPin, Edit3, Trash2, MoreVertical, X } from 'lucide-react'
import { useState } from 'react'
import { ActivityIcon, getColorClasses } from './ActivityIcon'

interface ActivityCardProps {
  activity: {
    id: number
    activity_type: {
      id: number
      name: string
      icon: string
      color: string
    }
    duration: number | null
    duration_unit: string
    distance: number | null
    calories: number
    notes: string | null
  }
  onEdit?: (id: number) => void
  onDelete?: (id: number) => void
  isViewingOthers?: boolean
  index?: number
}

export function ActivityCard({
  activity,
  onEdit,
  onDelete,
  isViewingOthers = false,
  index = 0
}: ActivityCardProps) {
  const [showMenu, setShowMenu] = useState(false)
  const colorClasses = getColorClasses(activity.activity_type.color)

  const formatDuration = () => {
    if (!activity.duration) return null
    if (activity.duration_unit === 'hours') {
      return `${activity.duration}h`
    }
    if (activity.duration >= 60) {
      const hours = Math.floor(activity.duration / 60)
      const mins = activity.duration % 60
      return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
    }
    return `${activity.duration}m`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, x: -100, scale: 0.9 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
      className="group relative"
    >
      <div className={`
        relative overflow-hidden rounded-xl
        bg-gradient-to-r from-white/[0.08] to-white/[0.02]
        border border-white/10
        hover:border-white/20
        transition-all duration-300
        hover:shadow-lg hover:shadow-black/20
      `}>
        {/* Left color accent */}
        <div className={`absolute left-0 top-0 bottom-0 w-1 ${colorClasses.bg}`} />

        <div className="p-4 pl-5 flex items-center gap-4">
          {/* Activity Icon */}
          <motion.div
            whileHover={{ scale: 1.1, rotate: 5 }}
            transition={{ type: 'spring', stiffness: 400 }}
          >
            <ActivityIcon
              icon={activity.activity_type.icon}
              color={activity.activity_type.color}
              size="md"
            />
          </motion.div>

          {/* Activity Details */}
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-white truncate">
              {activity.activity_type.name}
            </h4>
            <div className="flex items-center gap-3 mt-1 text-sm text-white/50">
              {formatDuration() && (
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  {formatDuration()}
                </span>
              )}
              {activity.distance && (
                <span className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5" />
                  {activity.distance} km
                </span>
              )}
            </div>
            {activity.notes && (
              <p className="text-xs text-white/40 mt-1 truncate">{activity.notes}</p>
            )}
          </div>

          {/* Calories Badge */}
          <div className="flex items-center gap-2">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: index * 0.05 + 0.2, type: 'spring' }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-orange-500/20 border border-orange-500/30"
            >
              <Flame className="w-4 h-4 text-orange-400" />
              <span className="text-sm font-semibold text-orange-300">
                {activity.calories}
              </span>
            </motion.div>

            {/* Actions - Inline Action Bar */}
            {!isViewingOthers && (onEdit || onDelete) && (
              <AnimatePresence mode="wait">
                {!showMenu ? (
                  // Ellipsis button (collapsed state)
                  <motion.button
                    key="ellipsis"
                    type="button"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={{ duration: 0.2 }}
                    onClick={(e) => {
                      e.preventDefault()
                      e.stopPropagation()
                      setShowMenu(true)
                    }}
                    className="p-2 rounded-lg text-white/40 hover:text-white hover:bg-white/10 transition-all"
                    aria-label="Show actions"
                  >
                    <MoreVertical className="w-4 h-4" />
                  </motion.button>
                ) : (
                  // Action bar (expanded state)
                  <motion.div
                    key="actions"
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                    transition={{ duration: 0.25, ease: 'easeOut' }}
                    className="flex items-center gap-1"
                  >
                    {onEdit && (
                      <>
                        <motion.button
                          type="button"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={(e) => {
                            e.preventDefault()
                            e.stopPropagation()
                            onEdit(activity.id)
                            setShowMenu(false)
                          }}
                          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-all text-xs"
                          aria-label="Edit activity"
                          title="Edit"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                          <span className="hidden sm:inline font-medium">Edit</span>
                        </motion.button>

                        {/* Vertical separator */}
                        <div className="w-px h-4 bg-white/10" />
                      </>
                    )}

                    {onDelete && (
                      <>
                        <motion.button
                          type="button"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={(e) => {
                            e.preventDefault()
                            e.stopPropagation()
                            onDelete(activity.id)
                            setShowMenu(false)
                          }}
                          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-all text-xs"
                          aria-label="Delete activity"
                          title="Delete"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                          <span className="hidden sm:inline font-medium">Delete</span>
                        </motion.button>

                        {/* Vertical separator */}
                        <div className="w-px h-4 bg-white/10" />
                      </>
                    )}

                    {/* Close button */}
                    <motion.button
                      type="button"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={(e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        setShowMenu(false)
                      }}
                      className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-white/50 hover:text-white hover:bg-white/10 transition-all text-xs"
                      aria-label="Close actions"
                      title="Close"
                    >
                      <X className="w-3.5 h-3.5" />
                    </motion.button>
                  </motion.div>
                )}
              </AnimatePresence>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Heart, Plus, FileText, AlertCircle, Check, Zap, Settings } from 'lucide-react'
import { api } from '../../api'
import { GlassCard, GlowButton } from '../ui'
import { ActivityCard } from './ActivityCard'
import { ActivityIcon, getColorClasses } from './ActivityIcon'
import { DailySummary } from './DailySummary'
import { ActivityLogModal } from './ActivityLogModal'
import { ManageFavoritesModal } from './ManageFavoritesModal'

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

interface HealthActivity {
  id: number
  activity_type: ActivityType
  duration: number | null
  duration_unit: string
  distance: number | null
  calories: number
  notes: string | null
  created_at: string
}

interface Favorite {
  id: number
  activity_type: ActivityType
  display_order: number
}

interface HealthSectionProps {
  groupId: number
  selectedDate: string
  isViewingOthers?: boolean
  userId?: number
  onActivitiesChange?: () => void
}

export function HealthSection({
  groupId,
  selectedDate,
  isViewingOthers = false,
  userId,
  onActivitiesChange
}: HealthSectionProps) {
  const [activities, setActivities] = useState<HealthActivity[]>([])
  const [summary, setSummary] = useState({ total_duration_minutes: 0, total_calories: 0, activity_count: 0 })
  const [legacyContent, setLegacyContent] = useState<string | null>(null)
  const [activityTypes, setActivityTypes] = useState<ActivityTypeGrouped[]>([])
  const [favorites, setFavorites] = useState<Favorite[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Modal states
  const [showLogModal, setShowLogModal] = useState(false)
  const [showFavoritesModal, setShowFavoritesModal] = useState(false)
  const [editingActivity, setEditingActivity] = useState<HealthActivity | null>(null)

  // Load activity types on mount
  useEffect(() => {
    loadActivityTypes()
    loadFavorites()
  }, [])

  // Load activities when group/date/user changes
  useEffect(() => {
    loadActivities()
  }, [groupId, selectedDate, userId])

  const loadActivityTypes = async () => {
    try {
      const data = await api.getActivityTypes()
      setActivityTypes(data)
    } catch (err) {
      console.error('Failed to load activity types:', err)
    }
  }

  const loadFavorites = async () => {
    try {
      const data = await api.getFavorites()
      setFavorites(data)
    } catch (err) {
      console.error('Failed to load favorites:', err)
    }
  }

  const loadActivities = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getHealthActivities(groupId, selectedDate, userId)
      setActivities(data.activities)
      setSummary(data.summary)
      setLegacyContent(data.legacy_content)
    } catch (err) {
      console.error('Failed to load health activities:', err)
      setError('Failed to load activities')
    } finally {
      setLoading(false)
    }
  }, [groupId, selectedDate, userId])

  const handleQuickLog = async (activityTypeId: number) => {
    setSaving(true)
    try {
      await api.quickLogActivity({
        group_id: groupId,
        activity_type_id: activityTypeId,
        entry_date: selectedDate
      })
      await loadActivities()
      onActivitiesChange?.()
    } catch (err) {
      console.error('Failed to quick log:', err)
      setError('Failed to log activity')
    } finally {
      setSaving(false)
    }
  }

  const handleCreateActivity = async (data: {
    activity_type_id: number
    duration?: number
    duration_unit?: string
    distance?: number
    notes?: string
  }) => {
    setSaving(true)
    try {
      await api.createHealthActivity({
        group_id: groupId,
        entry_date: selectedDate,
        ...data
      })
      await loadActivities()
      setShowLogModal(false)
      onActivitiesChange?.()
    } catch (err) {
      console.error('Failed to create activity:', err)
      throw err
    } finally {
      setSaving(false)
    }
  }

  const handleUpdateActivity = async (data: {
    activity_type_id: number
    duration?: number
    duration_unit?: string
    distance?: number
    notes?: string
  }) => {
    if (!editingActivity) return
    setSaving(true)
    try {
      await api.updateHealthActivity(editingActivity.id, {
        duration: data.duration,
        duration_unit: data.duration_unit,
        distance: data.distance,
        notes: data.notes
      })
      await loadActivities()
      setShowLogModal(false)
      setEditingActivity(null)
      onActivitiesChange?.()
    } catch (err) {
      console.error('Failed to update activity:', err)
      throw err
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteActivity = async (activityId: number) => {
    if (!confirm('Delete this activity?')) return
    try {
      await api.deleteHealthActivity(activityId)
      await loadActivities()
      onActivitiesChange?.()
    } catch (err) {
      console.error('Failed to delete activity:', err)
      setError('Failed to delete activity')
    }
  }

  const handleEditActivity = (activityId: number) => {
    const activity = activities.find(a => a.id === activityId)
    if (activity) {
      setEditingActivity(activity)
      setShowLogModal(true)
    }
  }

  const handleAddFavorite = async (activityTypeId: number) => {
    await api.addFavorite(activityTypeId)
    await loadFavorites()
  }

  const handleRemoveFavorite = async (activityTypeId: number) => {
    await api.removeFavorite(activityTypeId)
    await loadFavorites()
  }

  const hasActivities = activities.length > 0

  return (
    <GlassCard
      className="relative overflow-hidden"
      style={{
        background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, transparent 50%)'
      }}
    >
      {/* Left color accent */}
      <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-emerald-500 to-teal-500" />

      <div className="pl-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <motion.div
              whileHover={{ scale: 1.1, rotate: 5 }}
              className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/30"
            >
              <Heart className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </motion.div>
            <div>
              <h3 className="text-lg font-semibold text-white">Health</h3>
              <p className="text-white/40 text-sm">
                {hasActivities
                  ? `${activities.length} ${activities.length === 1 ? 'activity' : 'activities'} logged`
                  : 'No activities yet'}
              </p>
            </div>
          </div>

          {/* Right side: Quick Log + favorites + Add Activity + Gear + Check */}
          <div className="flex items-center gap-2">
            {!isViewingOthers && (
              <>
                {/* Quick Log Label */}
                <div className="hidden sm:flex items-center gap-1.5 mr-1">
                  <Zap className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-xs font-medium text-white/40 uppercase tracking-wider">Quick</span>
                </div>

                {/* Favorite Activity Buttons */}
                <div className="flex items-center gap-1.5 overflow-x-auto max-w-[200px] sm:max-w-none">
                  {favorites.slice(0, 3).map((fav, index) => {
                    const colorClasses = getColorClasses(fav.activity_type.color)
                    return (
                      <motion.button
                        key={fav.id}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: index * 0.05 }}
                        whileHover={{ scale: 1.08 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleQuickLog(fav.activity_type.id)}
                        disabled={loading || saving}
                        className={`
                          flex items-center gap-1.5 px-2 py-1.5 rounded-lg
                          bg-white/5 border ${colorClasses.border}
                          hover:bg-white/10
                          transition-all duration-200
                          disabled:opacity-50 disabled:cursor-not-allowed
                          flex-shrink-0
                        `}
                        title={`Quick log ${fav.activity_type.name}`}
                      >
                        <ActivityIcon
                          icon={fav.activity_type.icon}
                          color={fav.activity_type.color}
                          size="sm"
                          variant="ghost"
                        />
                        <span className="hidden sm:inline text-xs font-medium text-white/70">
                          {fav.activity_type.name.split(' ')[0]}
                        </span>
                      </motion.button>
                    )
                  })}
                </div>

                {/* Add Activity Button */}
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => {
                    setEditingActivity(null)
                    setShowLogModal(true)
                  }}
                  disabled={loading}
                  className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-emerald-500/20 border border-emerald-500/30 hover:bg-emerald-500/30 hover:border-emerald-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Add new activity"
                >
                  <Plus className="w-4 h-4 text-emerald-400" />
                  <span className="hidden sm:inline text-sm font-medium text-emerald-300">Add</span>
                </motion.button>

                {/* Settings/Gear Button */}
                <motion.button
                  whileHover={{ scale: 1.05, rotate: 90 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowFavoritesModal(true)}
                  disabled={loading}
                  className="p-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Manage favorites"
                >
                  <Settings className="w-4 h-4 text-white/50" />
                </motion.button>
              </>
            )}

            {/* Completion indicator */}
            {hasActivities && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
              >
                <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center">
                  <Check className="w-4 h-4 text-emerald-400" />
                </div>
              </motion.div>
            )}
          </div>
        </div>

        {/* Error Message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-4 p-3 rounded-lg bg-red-500/20 border border-red-500/30 flex items-center gap-2 text-red-300 text-sm"
            >
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Loading State */}
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="w-8 h-8 rounded-full border-2 border-emerald-500/30 border-t-emerald-500 animate-spin" />
          </div>
        ) : (
          <>
            {/* Activities List */}
            {hasActivities && (
              <div className="space-y-3 mb-4">
                <AnimatePresence>
                  {activities.map((activity, index) => (
                    <ActivityCard
                      key={activity.id}
                      activity={activity}
                      onEdit={handleEditActivity}
                      onDelete={handleDeleteActivity}
                      isViewingOthers={isViewingOthers}
                      index={index}
                    />
                  ))}
                </AnimatePresence>
              </div>
            )}

            {/* Daily Summary */}
            {hasActivities && (
              <DailySummary summary={summary} />
            )}

            {/* Empty State */}
            {!hasActivities && !legacyContent && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-8"
              >
                <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-emerald-500/10 flex items-center justify-center">
                  <Heart className="w-8 h-8 text-emerald-500/50" />
                </div>
                <p className="text-white/50 mb-4">
                  {isViewingOthers
                    ? 'No activities logged for this day'
                    : 'Start tracking your health activities!'}
                </p>
                {!isViewingOthers && (
                  <GlowButton
                    variant="success"
                    icon={Plus}
                    onClick={() => {
                      setEditingActivity(null)
                      setShowLogModal(true)
                    }}
                  >
                    Log First Activity
                  </GlowButton>
                )}
              </motion.div>
            )}

            {/* Legacy Content (old text-based entries) */}
            {legacyContent && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4 p-4 rounded-xl bg-white/5 border border-white/10"
              >
                <div className="flex items-center gap-2 mb-2 text-white/50">
                  <FileText className="w-4 h-4" />
                  <span className="text-xs uppercase tracking-wider">Previous Entry</span>
                </div>
                <p className="text-white/70 whitespace-pre-wrap text-sm">
                  {legacyContent}
                </p>
              </motion.div>
            )}
          </>
        )}
      </div>

      {/* Activity Log Modal */}
      <ActivityLogModal
        isOpen={showLogModal}
        onClose={() => {
          setShowLogModal(false)
          setEditingActivity(null)
        }}
        onSubmit={editingActivity ? handleUpdateActivity : handleCreateActivity}
        activityTypes={activityTypes}
        editingActivity={editingActivity}
        loading={saving}
      />

      {/* Manage Favorites Modal */}
      <ManageFavoritesModal
        isOpen={showFavoritesModal}
        onClose={() => setShowFavoritesModal(false)}
        activityTypes={activityTypes}
        favorites={favorites}
        onAddFavorite={handleAddFavorite}
        onRemoveFavorite={handleRemoveFavorite}
        loading={saving}
      />
    </GlassCard>
  )
}

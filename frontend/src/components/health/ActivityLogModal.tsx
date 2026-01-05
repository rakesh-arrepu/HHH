import { useState, useEffect, useMemo } from 'react'
import { createPortal } from 'react-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Search, Clock, MapPin, FileText, Flame, ChevronDown } from 'lucide-react'
import { GlowButton } from '../ui'
import { ActivityIcon, getColorClasses } from './ActivityIcon'
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

interface ActivityLogModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: {
    activity_type_id: number
    duration?: number
    duration_unit?: string
    distance?: number
    notes?: string
  }) => Promise<void>
  activityTypes: ActivityTypeGrouped[]
  editingActivity?: {
    id: number
    activity_type: ActivityType
    duration: number | null
    duration_unit: string
    distance: number | null
    notes: string | null
  } | null
  loading?: boolean
}

export function ActivityLogModal({
  isOpen,
  onClose,
  onSubmit,
  activityTypes,
  editingActivity,
  loading = false
}: ActivityLogModalProps) {
  const [selectedType, setSelectedType] = useState<ActivityType | null>(null)
  const [duration, setDuration] = useState<string>('')
  const [durationUnit, setDurationUnit] = useState<'minutes' | 'hours'>('minutes')
  const [distance, setDistance] = useState<string>('')
  const [notes, setNotes] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null)
  const [showTypeSelector, setShowTypeSelector] = useState(true)

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      if (editingActivity) {
        setSelectedType(editingActivity.activity_type)
        setDuration(editingActivity.duration?.toString() || '')
        setDurationUnit((editingActivity.duration_unit as 'minutes' | 'hours') || 'minutes')
        setDistance(editingActivity.distance?.toString() || '')
        setNotes(editingActivity.notes || '')
        setShowTypeSelector(false)
      } else {
        setSelectedType(null)
        setDuration('')
        setDurationUnit('minutes')
        setDistance('')
        setNotes('')
        setSearchQuery('')
        setShowTypeSelector(true)
      }
    }
  }, [isOpen, editingActivity])

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

  // Calculate estimated calories
  const estimatedCalories = useMemo(() => {
    if (!selectedType) return 0
    const durationMins = durationUnit === 'hours'
      ? parseFloat(duration || '0') * 60
      : parseFloat(duration || selectedType.default_duration.toString())
    return Math.round(selectedType.met_value * 70 * (durationMins / 60))
  }, [selectedType, duration, durationUnit])

  const handleSubmit = async () => {
    if (!selectedType) return

    await onSubmit({
      activity_type_id: selectedType.id,
      duration: duration ? parseFloat(duration) : undefined,
      duration_unit: durationUnit,
      distance: distance ? parseFloat(distance) : undefined,
      notes: notes.trim() || undefined
    })
  }

  const handleSelectType = (type: ActivityType) => {
    setSelectedType(type)
    setDuration(type.default_duration.toString())
    setShowTypeSelector(false)
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
            <h2 className="text-lg font-semibold text-white">
              {editingActivity ? 'Edit Activity' : 'Log Activity'}
            </h2>
            <button
              onClick={onClose}
              className="p-2 rounded-lg text-white/50 hover:text-white hover:bg-white/10 transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-4 overflow-y-auto max-h-[calc(85vh-140px)]">
            {/* Activity Type Selector */}
            {showTypeSelector ? (
              <div className="space-y-4">
                {/* Search */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
                  <input
                    type="text"
                    placeholder="Search activities..."
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-emerald-500/50 transition-all"
                    autoFocus
                  />
                </div>

                {/* Categories */}
                <div className="space-y-2">
                  {filteredTypes.map(group => (
                    <div key={group.category} className="rounded-xl border border-white/10 overflow-hidden">
                      <button
                        onClick={() => setExpandedCategory(
                          expandedCategory === group.category ? null : group.category
                        )}
                        className="w-full flex items-center justify-between p-3 bg-white/5 hover:bg-white/10 transition-all"
                      >
                        <span className="font-medium text-white/80">
                          {CATEGORY_LABELS[group.category] || group.category}
                        </span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-white/40">
                            {group.activities.length} activities
                          </span>
                          <motion.div
                            animate={{ rotate: expandedCategory === group.category ? 180 : 0 }}
                          >
                            <ChevronDown className="w-4 h-4 text-white/40" />
                          </motion.div>
                        </div>
                      </button>

                      <AnimatePresence>
                        {expandedCategory === group.category && (
                          <motion.div
                            initial={{ height: 0 }}
                            animate={{ height: 'auto' }}
                            exit={{ height: 0 }}
                            className="overflow-hidden"
                          >
                            <div className="p-2 grid grid-cols-2 gap-2">
                              {group.activities.map(activity => {
                                const colorClasses = getColorClasses(activity.color)
                                return (
                                  <motion.button
                                    key={activity.id}
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={() => handleSelectType(activity)}
                                    className={`
                                      flex items-center gap-2 p-2 rounded-lg
                                      bg-white/5 border ${colorClasses.border}
                                      hover:bg-white/10 transition-all text-left
                                    `}
                                  >
                                    <ActivityIcon
                                      icon={activity.icon}
                                      color={activity.color}
                                      size="sm"
                                    />
                                    <span className="text-sm text-white truncate">
                                      {activity.name}
                                    </span>
                                  </motion.button>
                                )
                              })}
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Selected Activity */}
                {selectedType && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10"
                  >
                    <ActivityIcon
                      icon={selectedType.icon}
                      color={selectedType.color}
                      size="lg"
                    />
                    <div className="flex-1">
                      <h3 className="font-semibold text-white">{selectedType.name}</h3>
                      <p className="text-xs text-white/50">
                        {CATEGORY_LABELS[selectedType.category] || selectedType.category}
                      </p>
                    </div>
                    {!editingActivity && (
                      <button
                        onClick={() => setShowTypeSelector(true)}
                        className="text-sm text-emerald-400 hover:text-emerald-300"
                      >
                        Change
                      </button>
                    )}
                  </motion.div>
                )}

                {/* Duration */}
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-white/60 mb-2">
                    <Clock className="w-4 h-4" />
                    Duration
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      value={duration}
                      onChange={e => setDuration(e.target.value)}
                      placeholder={selectedType?.default_duration.toString() || '30'}
                      min="0"
                      className="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-emerald-500/50 transition-all"
                    />
                    <select
                      value={durationUnit}
                      onChange={e => setDurationUnit(e.target.value as 'minutes' | 'hours')}
                      className="px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:border-emerald-500/50 transition-all"
                    >
                      <option value="minutes">min</option>
                      <option value="hours">hr</option>
                    </select>
                  </div>
                </div>

                {/* Distance (optional) */}
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-white/60 mb-2">
                    <MapPin className="w-4 h-4" />
                    Distance (optional)
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      value={distance}
                      onChange={e => setDistance(e.target.value)}
                      placeholder="0"
                      min="0"
                      step="0.1"
                      className="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-emerald-500/50 transition-all"
                    />
                    <span className="text-white/50">km</span>
                  </div>
                </div>

                {/* Notes */}
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-white/60 mb-2">
                    <FileText className="w-4 h-4" />
                    Notes (optional)
                  </label>
                  <textarea
                    value={notes}
                    onChange={e => setNotes(e.target.value)}
                    placeholder="How was your workout?"
                    rows={2}
                    maxLength={500}
                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-emerald-500/50 transition-all resize-none"
                  />
                </div>

                {/* Estimated Calories */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex items-center justify-center gap-3 p-4 rounded-xl bg-gradient-to-r from-orange-500/20 to-amber-500/20 border border-orange-500/30"
                >
                  <Flame className="w-6 h-6 text-orange-400" />
                  <div className="text-center">
                    <span className="text-2xl font-bold text-orange-300">
                      {estimatedCalories}
                    </span>
                    <span className="text-sm text-orange-300/60 ml-1">cal</span>
                  </div>
                  <span className="text-xs text-orange-300/50">estimated</span>
                </motion.div>
              </div>
            )}
          </div>

          {/* Footer */}
          {!showTypeSelector && (
            <div className="p-4 border-t border-white/10 flex gap-3">
              <GlowButton
                variant="ghost"
                onClick={onClose}
                className="flex-1"
              >
                Cancel
              </GlowButton>
              <GlowButton
                variant="success"
                onClick={handleSubmit}
                loading={loading}
                disabled={!selectedType}
                className="flex-1"
              >
                {editingActivity ? 'Update' : 'Log Activity'}
              </GlowButton>
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )

  return createPortal(modalContent, document.body)
}

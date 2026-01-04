import { useState, useEffect, useRef } from 'react'
import { api } from '../api'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Heart,
  Smile,
  Coins,
  Flame,
  Check,
  X,
  Edit3,
  Save,
  Sparkles,
  Users,
  PartyPopper,
  Calendar,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import {
  GlassCard,
  GlowButton,
  TextareaField,
  SelectField,
  PageContainer,
  ProgressBar,
  EmptyState
} from '../components/ui'
import { celebrateAllComplete, celebrateStreak } from '../components/ui/confetti'
import { MemberSelector, type Member } from '../components/MemberSelector'

type Group = { id: number; name: string; is_owner: boolean }

const SECTIONS = [
  {
    key: 'health',
    label: 'Health',
    icon: Heart,
    color: 'emerald',
    gradient: 'from-emerald-500 to-teal-500',
    glow: 'shadow-emerald-500/30',
    bgGlow: 'rgba(16, 185, 129, 0.1)',
  },
  {
    key: 'happiness',
    label: 'Happiness',
    icon: Smile,
    color: 'amber',
    gradient: 'from-amber-500 to-orange-500',
    glow: 'shadow-amber-500/30',
    bgGlow: 'rgba(245, 158, 11, 0.1)',
  },
  {
    key: 'hela',
    label: 'Hela (Money)',
    icon: Coins,
    color: 'yellow',
    gradient: 'from-yellow-500 to-amber-500',
    glow: 'shadow-yellow-500/30',
    bgGlow: 'rgba(234, 179, 8, 0.1)',
  },
]

// Helper to get today's date in YYYY-MM-DD format
const getTodayDate = () => new Date().toISOString().split('T')[0]

// Helper to format date for display
const formatDateDisplay = (dateStr: string, short = false) => {
  const date = new Date(dateStr + 'T00:00:00')
  if (short) {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    })
  }
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  })
}

// Helper to check if a date is in the future
const isFutureDate = (dateStr: string) => {
  const today = getTodayDate()
  return dateStr > today
}

export default function Journal() {
  const [groups, setGroups] = useState<Group[]>([])
  const [selectedGroup, setSelectedGroup] = useState<number | null>(null)
  const [entries, setEntries] = useState<Record<string, string>>({})
  const [streak, setStreak] = useState(0)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState<string | null>(null)
  const [selectedDate, setSelectedDate] = useState(getTodayDate())
  const [showDatePicker, setShowDatePicker] = useState(false)
  const [filledDates, setFilledDates] = useState<Set<string>>(new Set())
  const [selectedUserId, setSelectedUserId] = useState<number | undefined>(undefined)
  const [members, setMembers] = useState<Member[]>([])
  const [currentUserId, setCurrentUserId] = useState<number>(0)
  const prevCompleteRef = useRef(false)
  const datePickerRef = useRef<HTMLDivElement>(null)

  // Close date picker when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (datePickerRef.current && !datePickerRef.current.contains(event.target as Node)) {
        setShowDatePicker(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    loadGroups()
    loadCurrentUser()
  }, [])

  useEffect(() => {
    if (selectedGroup) {
      loadMembers()
      loadEntriesForDate(selectedDate, selectedUserId)
      loadStreak(selectedUserId)
      loadFilledDates(selectedUserId)
      // Reset selectedUserId when switching groups
      if (selectedUserId !== undefined) {
        setSelectedUserId(undefined)
      }
    }
  }, [selectedGroup])

  useEffect(() => {
    if (selectedGroup) {
      loadEntriesForDate(selectedDate, selectedUserId)
      loadStreak(selectedUserId)
      loadFilledDates(selectedUserId)
    }
  }, [selectedDate, selectedUserId])

  // Celebrate when all sections are completed
  const completedCount = Object.keys(entries).length
  const isComplete = completedCount === 3

  useEffect(() => {
    if (isComplete && !prevCompleteRef.current) {
      celebrateAllComplete()
    }
    prevCompleteRef.current = isComplete
  }, [isComplete])

  const loadGroups = async () => {
    try {
      const data = await api.getGroups()
      setGroups(data)
      if (data.length > 0) {
        setSelectedGroup(data[0].id)
      }
    } catch (err) {
      console.error('Failed to load groups:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadCurrentUser = async () => {
    try {
      const user = await api.getMe()
      setCurrentUserId(user.id)
    } catch (err) {
      console.error('Failed to load current user:', err)
    }
  }

  const loadMembers = async () => {
    if (!selectedGroup) return
    try {
      const data = await api.getMembers(selectedGroup)
      setMembers(data)
    } catch (err) {
      console.error('Failed to load members:', err)
    }
  }

  const loadEntriesForDate = async (date: string, userId?: number) => {
    if (!selectedGroup) return
    try {
      const data = await api.getEntries(selectedGroup, date, userId)
      const entriesMap: Record<string, string> = {}
      data.forEach((e) => {
        entriesMap[e.section] = e.content
      })
      setEntries(entriesMap)
    } catch (err) {
      console.error('Failed to load entries:', err)
    }
  }

  const loadFilledDates = async (userId?: number) => {
    if (!selectedGroup) return
    try {
      const history = await api.getHistory(selectedGroup, 90, userId)
      const dates = new Set<string>()
      history.forEach((day) => {
        if (day.completed_sections.length > 0) {
          dates.add(day.date)
        }
      })
      setFilledDates(dates)
    } catch (err) {
      console.error('Failed to load filled dates:', err)
    }
  }

  const loadStreak = async (userId?: number) => {
    if (!selectedGroup) return
    try {
      const data = await api.getStreak(selectedGroup, userId)
      setStreak(data.streak)
      if (data.streak > 0 && data.streak % 7 === 0) {
        setTimeout(() => celebrateStreak(data.streak), 500)
      }
    } catch (err) {
      console.error('Failed to load streak:', err)
    }
  }

  const saveEntry = async (section: string, content: string) => {
    if (!selectedGroup || !content.trim()) return

    setSaving(section)
    try {
      await api.createEntry({
        group_id: selectedGroup,
        section,
        content: content.trim(),
        entry_date: selectedDate,
      })
      setEntries((prev) => ({ ...prev, [section]: content.trim() }))
      setFilledDates((prev) => new Set([...prev, selectedDate]))
      loadStreak()
    } catch (err) {
      console.error('Failed to save entry:', err)
    } finally {
      setSaving(null)
    }
  }

  const navigateDate = (direction: 'prev' | 'next') => {
    const current = new Date(selectedDate + 'T00:00:00')
    if (direction === 'prev') {
      current.setDate(current.getDate() - 1)
    } else {
      current.setDate(current.getDate() + 1)
    }
    const newDate = current.toISOString().split('T')[0]
    if (!isFutureDate(newDate)) {
      setSelectedDate(newDate)
    }
  }

  const handleDateSelect = (dateStr: string) => {
    if (!isFutureDate(dateStr)) {
      setSelectedDate(dateStr)
      setShowDatePicker(false)
    }
  }

  const isToday = selectedDate === getTodayDate()
  const canGoNext = !isToday

  if (loading) {
    return (
      <PageContainer className="flex items-center justify-center min-h-[60vh]">
        <div className="spinner" />
      </PageContainer>
    )
  }

  if (groups.length === 0) {
    return (
      <PageContainer>
        <EmptyState
          icon={Users}
          title="No Groups Yet"
          description="Create a group to start tracking your daily HHH entries with friends."
          action={
            <Link to="/groups">
              <GlowButton icon={Sparkles}>Create Your First Group</GlowButton>
            </Link>
          }
        />
      </PageContainer>
    )
  }

  const groupOptions = groups.map((g) => ({ value: g.id, label: g.name }))

  const currentGroup = groups.find(g => g.id === selectedGroup)
  const isOwner = currentGroup?.is_owner || false
  const isViewingOthers = selectedUserId !== undefined

  return (
    <PageContainer>
      {/* Top Bar: Group + Member Selector + Streak */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 mb-6">
        <div className="flex-1 max-w-[200px]">
          <SelectField
            options={groupOptions}
            value={selectedGroup || ''}
            onChange={(e) => setSelectedGroup(Number(e.target.value))}
            icon={Users}
          />
        </div>

        {isOwner && members.length > 0 && (
          <div className="flex-1 max-w-[250px]">
            <MemberSelector
              members={members}
              selectedUserId={selectedUserId}
              onSelectUser={setSelectedUserId}
              currentUserId={currentUserId}
              isOwner={isOwner}
            />
          </div>
        )}

        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', bounce: 0.5, delay: 0.2 }}
          className={`streak-fire ${completedCount >= 2 ? 'streak-success' : ''}`}
        >
          <Flame className={`w-5 h-5 fire-icon ${completedCount >= 2 ? 'text-emerald-400' : 'text-orange-400'}`} />
          <span className={`text-xl font-bold bg-gradient-to-r ${completedCount >= 2 ? 'from-emerald-400 via-teal-400 to-cyan-400' : 'from-orange-400 via-amber-400 to-yellow-400'} bg-clip-text text-transparent`}>
            {streak}
          </span>
          <span className="text-white/60 text-xs hidden sm:inline">day streak</span>
        </motion.div>
      </div>

      {/* Date Navigator - Standalone Section with Higher Z-Index */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mb-6 relative"
        style={{ zIndex: 100 }}
        ref={datePickerRef}
      >
        <GlassCard className="p-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            {/* Date Controls */}
            <div className="flex items-center gap-2 flex-wrap">
              <button
                onClick={() => navigateDate('prev')}
                className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-white/60 hover:text-white transition-all"
                title="Previous day"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>

              <button
                onClick={() => setShowDatePicker(!showDatePicker)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/30 hover:border-purple-500/50 transition-all"
              >
                <Calendar className="w-5 h-5 text-purple-400" />
                <span className="text-white font-medium">
                  {isToday ? 'Today' : formatDateDisplay(selectedDate, true)}
                </span>
              </button>

              <button
                onClick={() => navigateDate('next')}
                disabled={!canGoNext}
                className={`p-2 rounded-lg transition-all ${
                  canGoNext
                    ? 'bg-white/5 hover:bg-white/10 text-white/60 hover:text-white'
                    : 'bg-white/5 text-white/20 cursor-not-allowed'
                }`}
                title="Next day"
              >
                <ChevronRight className="w-5 h-5" />
              </button>

              {!isToday && (
                <button
                  onClick={() => setSelectedDate(getTodayDate())}
                  className="px-3 py-2 text-sm rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 hover:text-emerald-300 border border-emerald-500/30 transition-all"
                >
                  Today
                </button>
              )}
            </div>

            {/* Progress Stats */}
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-white/50 text-xs uppercase tracking-wide">Progress</p>
                <p className="text-white font-bold">
                  <span className="text-2xl">{completedCount}</span>
                  <span className="text-white/50 text-lg">/3</span>
                </p>
              </div>
              <div className="w-24 sm:w-32">
                <ProgressBar value={completedCount} max={3} size="md" />
              </div>
            </div>
          </div>

          {/* Date Display */}
          <div className="mt-3 pt-3 border-t border-white/10">
            <p className="text-white/60 text-sm text-center">
              {formatDateDisplay(selectedDate)}
              {isComplete && (
                <span className="ml-2 text-emerald-400">
                  <Check className="w-4 h-4 inline" /> Complete!
                </span>
              )}
            </p>
          </div>

          {/* Date Picker Dropdown - Positioned Absolutely */}
          <AnimatePresence>
            {showDatePicker && (
              <motion.div
                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                className="absolute left-4 top-full mt-2"
                style={{ zIndex: 1000 }}
              >
                <DatePickerCalendar
                  selectedDate={selectedDate}
                  onSelect={handleDateSelect}
                  filledDates={filledDates}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </GlassCard>
      </motion.div>

      {/* Celebration Banner */}
      <AnimatePresence>
        {isComplete && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-6"
          >
            <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-500/20 via-teal-500/20 to-cyan-500/20 border border-emerald-500/30">
              <div className="flex items-center justify-center gap-3">
                <PartyPopper className="w-6 h-6 text-emerald-400" />
                <span className="celebration-text font-semibold text-lg">
                  All sections complete for {isToday ? 'today' : formatDateDisplay(selectedDate, true)}!
                </span>
                <PartyPopper className="w-6 h-6 text-emerald-400" />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Entry Cards */}
      <div className="grid gap-4 sm:gap-6">
        {SECTIONS.map((section, index) => (
          <motion.div
            key={section.key}
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 + index * 0.1 }}
          >
            <EntryCard
              section={section}
              content={entries[section.key] || ''}
              onSave={(content) => saveEntry(section.key, content)}
              saving={saving === section.key}
              isViewingOthers={isViewingOthers}
            />
          </motion.div>
        ))}
      </div>
    </PageContainer>
  )
}

function EntryCard({
  section,
  content,
  onSave,
  saving,
  isViewingOthers = false,
}: {
  section: {
    key: string
    label: string
    icon: typeof Heart
    color: string
    gradient: string
    glow: string
    bgGlow: string
  }
  content: string
  onSave: (content: string) => void
  saving: boolean
  isViewingOthers?: boolean
}) {
  const [text, setText] = useState(content)
  const [editing, setEditing] = useState(false)

  useEffect(() => {
    setText(content)
  }, [content])

  const hasContent = content.trim().length > 0
  const isDirty = text !== content
  const Icon = section.icon

  const handleSave = () => {
    onSave(text)
    setEditing(false)
  }

  const handleCancel = () => {
    setText(content)
    setEditing(false)
  }

  return (
    <GlassCard
      className="relative overflow-hidden"
      style={{
        background: `linear-gradient(135deg, ${section.bgGlow} 0%, transparent 50%)`,
      }}
    >
      {/* Color accent bar */}
      <div
        className={`absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b ${section.gradient}`}
      />

      <div className="pl-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <motion.div
              whileHover={{ scale: 1.1, rotate: 5 }}
              className={`w-12 h-12 rounded-xl bg-gradient-to-br ${section.gradient} flex items-center justify-center shadow-lg ${section.glow}`}
            >
              <Icon className="w-6 h-6 text-white" />
            </motion.div>
            <div>
              <h3 className="text-lg font-semibold text-white">{section.label}</h3>
              <p className="text-white/40 text-sm">
                {hasContent ? 'Completed' : 'Not logged yet'}
              </p>
            </div>
          </div>

          {hasContent && !editing && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="flex items-center gap-2"
            >
              <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center">
                <Check className="w-4 h-4 text-emerald-400" />
              </div>
            </motion.div>
          )}
        </div>

        {/* Content */}
        <AnimatePresence mode="wait">
          {editing || !hasContent ? (
            <motion.div
              key="editing"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <TextareaField
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder={isViewingOthers ? 'Viewing another user\'s entry' : `What did you do for ${section.label.toLowerCase()} today?`}
                rows={4}
                className="mb-4"
                disabled={isViewingOthers}
              />
              {!isViewingOthers && (
                <div className="flex justify-end gap-3">
                  {hasContent && (
                    <GlowButton
                      variant="ghost"
                      icon={X}
                      onClick={handleCancel}
                    >
                      Cancel
                    </GlowButton>
                  )}
                  <GlowButton
                    variant="success"
                    icon={Save}
                    onClick={handleSave}
                    loading={saving}
                    disabled={!text.trim() || !isDirty}
                  >
                    {saving ? 'Saving...' : 'Save Entry'}
                  </GlowButton>
                </div>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="viewing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <p className="text-white/80 whitespace-pre-wrap leading-relaxed mb-4">
                {content}
              </p>
              {!isViewingOthers && (
                <GlowButton
                  variant="ghost"
                  size="sm"
                  icon={Edit3}
                  onClick={() => setEditing(true)}
                >
                  Edit Entry
                </GlowButton>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </GlassCard>
  )
}

// Mini Calendar for Date Picker
function DatePickerCalendar({
  selectedDate,
  onSelect,
  filledDates,
}: {
  selectedDate: string
  onSelect: (date: string) => void
  filledDates: Set<string>
}) {
  const [viewDate, setViewDate] = useState(() => {
    const d = new Date(selectedDate + 'T00:00:00')
    return { year: d.getFullYear(), month: d.getMonth() }
  })

  const today = getTodayDate()

  const getDaysInMonth = (year: number, month: number) => {
    return new Date(year, month + 1, 0).getDate()
  }

  const getFirstDayOfMonth = (year: number, month: number) => {
    return new Date(year, month, 1).getDay()
  }

  const navigateMonth = (direction: 'prev' | 'next') => {
    setViewDate((prev) => {
      let newMonth = prev.month + (direction === 'next' ? 1 : -1)
      let newYear = prev.year

      if (newMonth > 11) {
        newMonth = 0
        newYear++
      } else if (newMonth < 0) {
        newMonth = 11
        newYear--
      }

      return { year: newYear, month: newMonth }
    })
  }

  const daysInMonth = getDaysInMonth(viewDate.year, viewDate.month)
  const firstDay = getFirstDayOfMonth(viewDate.year, viewDate.month)
  const monthName = new Date(viewDate.year, viewDate.month).toLocaleDateString('en-US', {
    month: 'long',
    year: 'numeric',
  })

  const days = []
  for (let i = 0; i < firstDay; i++) {
    days.push(<div key={`empty-${i}`} className="w-9 h-9" />)
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${viewDate.year}-${String(viewDate.month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    const isFuture = dateStr > today
    const isSelected = dateStr === selectedDate
    const isFilled = filledDates.has(dateStr)
    const isCurrentDay = dateStr === today

    days.push(
      <button
        key={day}
        onClick={() => !isFuture && onSelect(dateStr)}
        disabled={isFuture}
        className={`w-9 h-9 text-sm rounded-lg flex items-center justify-center transition-all relative ${
          isFuture
            ? 'text-white/20 cursor-not-allowed'
            : isSelected
            ? 'bg-purple-500 text-white font-bold shadow-lg shadow-purple-500/30'
            : isCurrentDay
            ? 'bg-purple-500/30 text-purple-300 font-semibold ring-2 ring-purple-500'
            : isFilled
            ? 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30'
            : 'text-white/60 hover:bg-white/10 hover:text-white'
        }`}
        title={isFuture ? 'Cannot fill future dates' : isFilled ? 'Has entries' : 'No entries'}
      >
        {day}
        {isFilled && !isSelected && (
          <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-emerald-500 rounded-full" />
        )}
      </button>
    )
  }

  return (
    <div className="bg-[#1a1a2e] p-4 rounded-xl border border-white/20 shadow-2xl min-w-[300px]"
         style={{ backdropFilter: 'blur(20px)' }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={() => navigateMonth('prev')}
          className="p-2 rounded-lg hover:bg-white/10 text-white/60 hover:text-white transition-all"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        <span className="text-white font-semibold">{monthName}</span>
        <button
          onClick={() => navigateMonth('next')}
          className="p-2 rounded-lg hover:bg-white/10 text-white/60 hover:text-white transition-all"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      {/* Day labels */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map((d) => (
          <div key={d} className="w-9 h-8 text-xs text-white/40 flex items-center justify-center font-medium">
            {d}
          </div>
        ))}
      </div>

      {/* Days grid */}
      <div className="grid grid-cols-7 gap-1">{days}</div>

      {/* Legend */}
      <div className="mt-4 pt-3 border-t border-white/10 flex items-center justify-center gap-6 text-xs text-white/50">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 bg-emerald-500 rounded-full" />
          <span>Has entries</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 bg-purple-500 rounded-full" />
          <span>Selected</span>
        </div>
      </div>
    </div>
  )
}

import { useState, useEffect } from 'react'
import { api } from '../api'
import { motion } from 'framer-motion'
import {
  CalendarDays,
  TrendingUp,
  Percent,
  Users,
  Heart,
  Smile,
  Coins,
  Check,
  Minus,
  ChevronLeft,
  ChevronRight,
  Calendar
} from 'lucide-react'
import {
  GlassCard,
  SelectField,
  PageContainer,
  PageTitle,
  EmptyState
} from '../components/ui'

type Group = { id: number; name: string }
type HistoryDay = { date: string; completed_sections: string[]; is_complete: boolean }

export default function History() {
  const [groups, setGroups] = useState<Group[]>([])
  const [selectedGroup, setSelectedGroup] = useState<number | null>(null)
  const [history, setHistory] = useState<HistoryDay[]>([])
  const [loading, setLoading] = useState(true)
  const [hoveredDay, setHoveredDay] = useState<HistoryDay | null>(null)

  // Month/Year picker state
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth()) // 0-11
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear())

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]

  useEffect(() => {
    loadGroups()
  }, [])

  useEffect(() => {
    if (selectedGroup) {
      loadHistory()
    }
  }, [selectedGroup, selectedMonth, selectedYear])

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

  const loadHistory = async () => {
    if (!selectedGroup) return

    // Calculate days in selected month
    const daysInMonth = new Date(selectedYear, selectedMonth + 1, 0).getDate()

    try {
      const data = await api.getHistory(selectedGroup, daysInMonth)

      // Filter history to only include dates from selected month
      const filteredHistory = data.filter(day => {
        const dayDate = new Date(day.date)
        return dayDate.getMonth() === selectedMonth && dayDate.getFullYear() === selectedYear
      })

      setHistory(filteredHistory)
    } catch (err) {
      console.error('Failed to load history:', err)
    }
  }

  const goToPreviousMonth = () => {
    if (selectedMonth === 0) {
      setSelectedMonth(11)
      setSelectedYear(selectedYear - 1)
    } else {
      setSelectedMonth(selectedMonth - 1)
    }
  }

  const goToNextMonth = () => {
    const currentDate = new Date()
    const isCurrentMonth = selectedMonth === currentDate.getMonth() && selectedYear === currentDate.getFullYear()

    // Don't allow going to future months
    if (isCurrentMonth) return

    if (selectedMonth === 11) {
      setSelectedMonth(0)
      setSelectedYear(selectedYear + 1)
    } else {
      setSelectedMonth(selectedMonth + 1)
    }
  }

  const goToCurrentMonth = () => {
    const now = new Date()
    setSelectedMonth(now.getMonth())
    setSelectedYear(now.getFullYear())
  }

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
          icon={CalendarDays}
          title="No Groups Found"
          description="Create a group first to start tracking your history"
        />
      </PageContainer>
    )
  }

  // Calculate stats
  const daysInMonth = new Date(selectedYear, selectedMonth + 1, 0).getDate()
  const currentDate = new Date()
  const isCurrentMonth = selectedMonth === currentDate.getMonth() && selectedYear === currentDate.getFullYear()

  const completeDays = history.filter((d) => d.is_complete).length
  const partialDays = history.filter(
    (d) => d.completed_sections.length > 0 && !d.is_complete
  ).length
  const completionRate = daysInMonth > 0 ? Math.round((completeDays / daysInMonth) * 100) : 0

  const stats = [
    {
      label: 'Complete Days',
      value: completeDays,
      icon: Check,
      gradient: 'from-emerald-500 to-teal-500',
      glow: 'shadow-emerald-500/30',
    },
    {
      label: 'Partial Days',
      value: partialDays,
      icon: Minus,
      gradient: 'from-amber-500 to-orange-500',
      glow: 'shadow-amber-500/30',
    },
    {
      label: 'Completion Rate',
      value: `${completionRate}%`,
      icon: Percent,
      gradient: 'from-purple-500 to-pink-500',
      glow: 'shadow-purple-500/30',
    },
  ]

  const groupOptions = groups.map((g) => ({ value: g.id, label: g.name }))

  const getSectionIcon = (section: string) => {
    switch (section) {
      case 'health':
        return Heart
      case 'happiness':
        return Smile
      case 'hela':
        return Coins
      default:
        return Check
    }
  }

  // Generate calendar days for the selected month
  const generateCalendarDays = () => {
    const firstDayOfMonth = new Date(selectedYear, selectedMonth, 1)
    const lastDayOfMonth = new Date(selectedYear, selectedMonth + 1, 0)
    const startDayOfWeek = firstDayOfMonth.getDay() // 0-6 (Sun-Sat)
    const totalDays = lastDayOfMonth.getDate()

    const calendarDays: (HistoryDay | null)[] = []

    // Add empty cells for days before the 1st
    for (let i = 0; i < startDayOfWeek; i++) {
      calendarDays.push(null)
    }

    // Add actual days of the month
    for (let day = 1; day <= totalDays; day++) {
      const dateStr = `${selectedYear}-${String(selectedMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
      const dayData = history.find(h => h.date === dateStr)

      calendarDays.push(dayData || {
        date: dateStr,
        completed_sections: [],
        is_complete: false
      })
    }

    return calendarDays
  }

  const calendarDays = generateCalendarDays()

  return (
    <PageContainer>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <PageTitle
          title="History"
          subtitle="Your monthly tracking journey"
          icon={CalendarDays}
        />
        <div className="w-full sm:w-48">
          <SelectField
            options={groupOptions}
            value={selectedGroup || ''}
            onChange={(e) => setSelectedGroup(Number(e.target.value))}
            icon={Users}
          />
        </div>
      </div>

      {/* Month/Year Navigation */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <GlassCard className="py-4">
          <div className="flex items-center justify-between gap-4">
            <button
              onClick={goToPreviousMonth}
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-white/70 hover:text-white transition-all"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-4 flex-1 justify-center">
              <div className="text-center">
                <div className="flex items-center gap-2 justify-center">
                  <Calendar className="w-5 h-5 text-purple-400" />
                  <h3 className="text-xl sm:text-2xl font-bold text-white">
                    {monthNames[selectedMonth]} {selectedYear}
                  </h3>
                </div>
                <p className="text-white/40 text-xs sm:text-sm mt-1">
                  {daysInMonth} days in this month
                </p>
              </div>

              {!isCurrentMonth && (
                <button
                  onClick={goToCurrentMonth}
                  className="px-3 py-1.5 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 text-sm transition-all border border-purple-500/30"
                >
                  Today
                </button>
              )}
            </div>

            <button
              onClick={goToNextMonth}
              disabled={isCurrentMonth}
              className={`p-2 rounded-lg transition-all ${
                isCurrentMonth
                  ? 'bg-white/5 text-white/30 cursor-not-allowed'
                  : 'bg-white/5 hover:bg-white/10 text-white/70 hover:text-white'
              }`}
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </GlassCard>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <GlassCard className="relative overflow-hidden">
              <div className="flex items-center gap-4">
                <div
                  className={`w-14 h-14 rounded-xl bg-gradient-to-br ${stat.gradient} flex items-center justify-center shadow-lg ${stat.glow}`}
                >
                  <stat.icon className="w-7 h-7 text-white" />
                </div>
                <div>
                  <p className="text-white/50 text-sm">{stat.label}</p>
                  <p className="text-3xl font-bold text-white">{stat.value}</p>
                </div>
              </div>
              {/* Background decoration */}
              <div
                className={`absolute -right-4 -bottom-4 w-24 h-24 rounded-full bg-gradient-to-br ${stat.gradient} opacity-10 blur-xl`}
              />
            </GlassCard>
          </motion.div>
        ))}
      </div>

      {/* Calendar Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <GlassCard>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-purple-400" />
              {monthNames[selectedMonth]} {selectedYear}
            </h2>
            {hoveredDay && (
              <motion.div
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-sm text-white/60"
              >
                {new Date(hoveredDay.date + 'T00:00:00').toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                })}{' '}
                - {hoveredDay.completed_sections.length}/3 sections
              </motion.div>
            )}
          </div>

          {/* Calendar Grid - Properly Centered */}
          <div className="flex justify-center">
            <div className="inline-block">
              {/* Day Headers */}
              <div className="grid grid-cols-7 gap-2 mb-2">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                  <div
                    key={day}
                    className="w-11 h-8 sm:w-14 sm:h-10 flex items-center justify-center text-xs sm:text-sm text-white/50 font-medium"
                  >
                    {day.substring(0, 2)}
                  </div>
                ))}
              </div>

              {/* Calendar Days */}
              <div className="grid grid-cols-7 gap-2">
                {calendarDays.map((day, index) => {
                  if (!day) {
                    // Empty cell before the 1st of the month
                    return <div key={`empty-${index}`} className="w-11 h-11 sm:w-14 sm:h-14" />
                  }

                  const date = new Date(day.date + 'T00:00:00')
                  const today = new Date()
                  today.setHours(0, 0, 0, 0)
                  const dayDate = new Date(day.date + 'T00:00:00')
                  dayDate.setHours(0, 0, 0, 0)
                  const isToday = dayDate.getTime() === today.getTime()
                  const sectionCount = day.completed_sections.length
                  const isFutureDate = dayDate > today

                  return (
                    <motion.div
                      key={day.date}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.3 + index * 0.01 }}
                      onMouseEnter={() => !isFutureDate && setHoveredDay(day)}
                      onMouseLeave={() => setHoveredDay(null)}
                      onClick={() => !isFutureDate && setHoveredDay(hoveredDay?.date === day.date ? null : day)}
                      className={`
                        w-11 h-11 sm:w-14 sm:h-14 rounded-xl flex flex-col items-center justify-center transition-all
                        ${isFutureDate ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}
                        ${
                          day.is_complete
                            ? 'bg-gradient-to-br from-emerald-500 to-teal-500 shadow-lg shadow-emerald-500/30'
                            : sectionCount === 2
                            ? 'bg-gradient-to-br from-amber-500 to-orange-500 shadow-lg shadow-amber-500/20'
                            : sectionCount === 1
                            ? 'bg-gradient-to-br from-amber-500/50 to-orange-500/50'
                            : 'bg-white/5 hover:bg-white/10'
                        }
                        ${isToday ? 'ring-2 ring-purple-500 ring-offset-2 ring-offset-[#0f0f1a]' : ''}
                      `}
                    >
                      {/* Date number */}
                      <span
                        className={`text-sm sm:text-base font-bold ${
                          sectionCount > 0 ? 'text-white' : 'text-white/50'
                        }`}
                      >
                        {date.getDate()}
                      </span>

                      {/* Section count */}
                      {!isFutureDate && (
                        <span
                          className={`text-[10px] sm:text-xs font-semibold ${
                            sectionCount === 3
                              ? 'text-emerald-100'
                              : sectionCount === 2
                              ? 'text-amber-100'
                              : sectionCount === 1
                              ? 'text-amber-200/80'
                              : 'text-white/30'
                          }`}
                        >
                          {sectionCount}/3
                        </span>
                      )}
                    </motion.div>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Legend */}
          <div className="flex flex-wrap justify-center gap-4 sm:gap-8 mt-8 pt-6 border-t border-white/10">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-md bg-gradient-to-br from-emerald-500 to-teal-500 shadow-lg shadow-emerald-500/30" />
              <span className="text-white/60 text-sm">Complete (3/3)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-md bg-gradient-to-br from-amber-500 to-orange-500" />
              <span className="text-white/60 text-sm">Almost (2/3)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-md bg-gradient-to-br from-amber-500/50 to-orange-500/50" />
              <span className="text-white/60 text-sm">Started (1/3)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-md bg-white/10" />
              <span className="text-white/60 text-sm">Empty</span>
            </div>
          </div>

          {/* Selected/Hovered day details */}
          {hoveredDay && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 p-4 rounded-xl bg-white/5 border border-white/10"
            >
              <p className="text-white font-medium mb-2">
                {new Date(hoveredDay.date + 'T00:00:00').toLocaleDateString('en-US', {
                  weekday: 'long',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
              {hoveredDay.completed_sections.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {hoveredDay.completed_sections.map((section) => {
                    const Icon = getSectionIcon(section)
                    return (
                      <div
                        key={section}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${
                          section === 'health'
                            ? 'bg-emerald-500/20 text-emerald-400'
                            : section === 'happiness'
                            ? 'bg-amber-500/20 text-amber-400'
                            : 'bg-yellow-500/20 text-yellow-400'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                        <span className="text-sm capitalize font-medium">{section}</span>
                      </div>
                    )
                  })}
                </div>
              ) : (
                <p className="text-white/40 text-sm">No entries for this day</p>
              )}
            </motion.div>
          )}
        </GlassCard>
      </motion.div>
    </PageContainer>
  )
}

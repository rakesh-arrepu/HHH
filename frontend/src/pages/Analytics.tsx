import { useState, useEffect } from 'react'
import { api } from '../api'
import { motion } from 'framer-motion'
import { useAuth } from '../auth'
import {
  BarChart3,
  Users,
  TrendingUp,
  Trophy,
  Flame,
  Target,
  Calendar,
  Heart,
  Smile,
  Coins,
  Crown,
  Medal,
  Award,
  Zap,
  ChevronLeft,
  ChevronRight,
  Clock,
  Activity,
  Dumbbell
} from 'lucide-react'
import {
  GlassCard,
  SelectField,
  PageContainer,
  PageTitle,
  EmptyState,
  Badge
} from '../components/ui'
import { ActivityIcon, getColorClasses } from '../components/health/ActivityIcon'

type Group = { id: number; name: string; owner_id: number; is_owner: boolean }
type Member = { id: number; user_id: number; name: string; email: string }
type HistoryDay = { date: string; completed_sections: string[]; is_complete: boolean }
type TabType = 'overview' | 'health'

interface HealthAnalytics {
  period: string
  summary: {
    total_activities: number
    total_duration_minutes: number
    total_calories: number
    active_days: number
  }
  activity_breakdown: {
    activity_type: {
      id: number
      name: string
      category: string
      icon: string
      color: string
      met_value: number
      default_duration: number
    }
    count: number
    duration: number
    calories: number
    percentage: number
  }[]
  daily_trend: {
    date: string
    calories: number
    duration_minutes: number
    activities: number
  }[]
  category_breakdown: {
    category: string
    count: number
    calories: number
  }[]
}

export default function Analytics() {
  const { user } = useAuth()
  const [groups, setGroups] = useState<Group[]>([])
  const [selectedGroup, setSelectedGroup] = useState<number | null>(null)
  const [members, setMembers] = useState<Member[]>([])
  const [history, setHistory] = useState<HistoryDay[]>([])
  const [streak, setStreak] = useState(0)
  const [loading, setLoading] = useState(true)

  // Tab state
  const [activeTab, setActiveTab] = useState<TabType>('overview')

  // Health analytics state
  const [healthAnalytics, setHealthAnalytics] = useState<HealthAnalytics | null>(null)
  const [healthPeriod, setHealthPeriod] = useState<'week' | 'month' | 'year'>('month')
  const [healthLoading, setHealthLoading] = useState(false)
  const [selectedMemberId, setSelectedMemberId] = useState<number | null>(null) // null = all members (group view)

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
      loadGroupData()
    }
  }, [selectedGroup, selectedMonth, selectedYear])

  useEffect(() => {
    if (selectedGroup && activeTab === 'health') {
      loadHealthAnalytics()
    }
  }, [selectedGroup, activeTab, healthPeriod, selectedMemberId])

  // Reset member selection when group changes
  useEffect(() => {
    if (selectedGroup && user) {
      const currentGroup = groups.find(g => g.id === selectedGroup)
      if (currentGroup && !currentGroup.is_owner) {
        // Non-owners can only see their own data
        setSelectedMemberId(user.id)
      } else {
        // Owners see all members by default
        setSelectedMemberId(null)
      }
    }
  }, [selectedGroup, groups, user])

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

  const loadGroupData = async () => {
    if (!selectedGroup) return

    // Calculate days in selected month
    const daysInMonth = new Date(selectedYear, selectedMonth + 1, 0).getDate()

    try {
      const [membersData, historyData, streakData] = await Promise.all([
        api.getMembers(selectedGroup),
        api.getHistory(selectedGroup, daysInMonth),
        api.getStreak(selectedGroup),
      ])
      setMembers(membersData)

      // Filter history to only include dates from selected month
      const filteredHistory = historyData.filter(day => {
        const dayDate = new Date(day.date)
        return dayDate.getMonth() === selectedMonth && dayDate.getFullYear() === selectedYear
      })

      setHistory(filteredHistory)
      setStreak(streakData.streak)
    } catch (err) {
      console.error('Failed to load group data:', err)
    }
  }

  const loadHealthAnalytics = async () => {
    if (!selectedGroup) return
    setHealthLoading(true)
    try {
      const data = await api.getHealthAnalytics(
        selectedGroup,
        healthPeriod,
        selectedMemberId !== null ? selectedMemberId : undefined
      )
      setHealthAnalytics(data)
    } catch (err) {
      console.error('Failed to load health analytics:', err)
    } finally {
      setHealthLoading(false)
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
          icon={BarChart3}
          title="No Groups Found"
          description="Create a group first to view analytics"
        />
      </PageContainer>
    )
  }

  const groupOptions = groups.map((g) => ({ value: g.id, label: g.name }))

  // Calculate days in the selected month
  const daysInMonth = new Date(selectedYear, selectedMonth + 1, 0).getDate()
  const currentDate = new Date()
  const isCurrentMonth = selectedMonth === currentDate.getMonth() && selectedYear === currentDate.getFullYear()

  // Calculate group-level stats
  const completeDays = history.filter((d) => d.is_complete).length
  const totalDays = daysInMonth
  const completionRate = totalDays > 0 ? Math.round((completeDays / totalDays) * 100) : 0
  const avgSectionsPerDay =
    history.length > 0
      ? (
          history.reduce((acc, d) => acc + d.completed_sections.length, 0) / history.length
        ).toFixed(1)
      : '0'

  // Section breakdown
  const healthCount = history.reduce(
    (acc, d) => acc + (d.completed_sections.includes('health') ? 1 : 0),
    0
  )
  const happinessCount = history.reduce(
    (acc, d) => acc + (d.completed_sections.includes('happiness') ? 1 : 0),
    0
  )
  const helaCount = history.reduce(
    (acc, d) => acc + (d.completed_sections.includes('hela') ? 1 : 0),
    0
  )

  const sectionStats = [
    {
      key: 'health',
      label: 'Health',
      count: healthCount,
      icon: Heart,
      gradient: 'from-emerald-500 to-teal-500',
      glow: 'shadow-emerald-500/30',
    },
    {
      key: 'happiness',
      label: 'Happiness',
      count: happinessCount,
      icon: Smile,
      gradient: 'from-amber-500 to-orange-500',
      glow: 'shadow-amber-500/30',
    },
    {
      key: 'hela',
      label: 'Hela (Money)',
      count: helaCount,
      icon: Coins,
      gradient: 'from-yellow-500 to-amber-500',
      glow: 'shadow-yellow-500/30',
    },
  ]

  // Weekly trend data
  const weeklyData = []
  for (let i = 0; i < 4; i++) {
    const weekStart = i * 7
    const weekEnd = (i + 1) * 7
    const weekDays = history.slice(weekStart, weekEnd)
    const weekComplete = weekDays.filter((d) => d.is_complete).length
    weeklyData.unshift({
      week: `Week ${4 - i}`,
      complete: weekComplete,
      total: weekDays.length,
      rate: weekDays.length > 0 ? Math.round((weekComplete / weekDays.length) * 100) : 0,
    })
  }

  // Format duration
  const formatDuration = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
  }

  // Category colors
  const categoryColors: Record<string, string> = {
    cardio: 'from-red-500 to-orange-500',
    sports: 'from-green-500 to-emerald-500',
    strength: 'from-purple-500 to-indigo-500',
    'mind-body': 'from-violet-500 to-purple-500',
    outdoor: 'from-teal-500 to-cyan-500',
    home: 'from-amber-500 to-yellow-500',
  }

  const categoryLabels: Record<string, string> = {
    cardio: 'Cardio',
    sports: 'Sports',
    strength: 'Strength & Fitness',
    'mind-body': 'Mind & Body',
    outdoor: 'Outdoor & Adventure',
    home: 'Home & Daily',
  }

  return (
    <PageContainer>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <PageTitle
          title="Analytics"
          subtitle="Track your progress and statistics"
          icon={BarChart3}
        />
        <div className="w-full sm:w-48">
          <SelectField
            label="Group"
            options={groupOptions}
            value={selectedGroup || ''}
            onChange={(e) => setSelectedGroup(Number(e.target.value))}
            icon={Users}
          />
        </div>
      </div>

      {/* Tab Selector */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <div className="flex gap-2 p-1 rounded-xl bg-white/5 border border-white/10 w-fit">
          <button
            onClick={() => setActiveTab('overview')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'overview'
                ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
                : 'text-white/60 hover:text-white hover:bg-white/10'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            HHH Overview
          </button>
          <button
            onClick={() => setActiveTab('health')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'health'
                ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg'
                : 'text-white/60 hover:text-white hover:bg-white/10'
            }`}
          >
            <Heart className="w-4 h-4" />
            Health Activities
          </button>
        </div>
      </motion.div>

      {/* Overview Tab Content */}
      {activeTab === 'overview' && (
        <>
          {/* Month/Year Picker */}
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

          {/* Key Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 mb-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <GlassCard className="text-center py-4 sm:py-6">
                <div className="w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-2 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center shadow-lg shadow-orange-500/30">
                  <Flame className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                </div>
                <p className="text-2xl sm:text-3xl font-bold text-white">{streak}</p>
                <p className="text-white/50 text-xs sm:text-sm">Day Streak</p>
              </GlassCard>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <GlassCard className="text-center py-4 sm:py-6">
                <div className="w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-2 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/30">
                  <Trophy className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                </div>
                <p className="text-2xl sm:text-3xl font-bold text-white">{completeDays}</p>
                <p className="text-white/50 text-xs sm:text-sm">Perfect Days</p>
              </GlassCard>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <GlassCard className="text-center py-4 sm:py-6">
                <div className="w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-2 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/30">
                  <Target className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                </div>
                <p className="text-2xl sm:text-3xl font-bold text-white">{completionRate}%</p>
                <p className="text-white/50 text-xs sm:text-sm">Completion</p>
              </GlassCard>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <GlassCard className="text-center py-4 sm:py-6">
                <div className="w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-2 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/30">
                  <Zap className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                </div>
                <p className="text-2xl sm:text-3xl font-bold text-white">{avgSectionsPerDay}</p>
                <p className="text-white/50 text-xs sm:text-sm">Avg/Day</p>
              </GlassCard>
            </motion.div>
          </div>

          {/* Section Breakdown */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mb-8"
          >
            <GlassCard>
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-400" />
                Section Breakdown ({monthNames[selectedMonth]})
              </h3>
              <div className="space-y-4">
                {sectionStats.map((section) => {
                  const percentage = Math.round((section.count / totalDays) * 100)
                  return (
                    <div key={section.key} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div
                            className={`w-8 h-8 rounded-lg bg-gradient-to-br ${section.gradient} flex items-center justify-center shadow-lg ${section.glow}`}
                          >
                            <section.icon className="w-4 h-4 text-white" />
                          </div>
                          <span className="text-white/80 text-sm">{section.label}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-white font-semibold">{section.count}</span>
                          <span className="text-white/40 text-sm">/ {totalDays} days</span>
                        </div>
                      </div>
                      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${percentage}%` }}
                          transition={{ duration: 0.8, delay: 0.6 }}
                          className={`h-full bg-gradient-to-r ${section.gradient} rounded-full`}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </GlassCard>
          </motion.div>

          {/* Weekly Trend */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="mb-8"
          >
            <GlassCard>
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-purple-400" />
                Weekly Trend
              </h3>
              <div className="grid grid-cols-4 gap-2 sm:gap-4">
                {weeklyData.map((week, index) => (
                  <motion.div
                    key={week.week}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.7 + index * 0.1 }}
                    className="text-center"
                  >
                    <div className="relative h-24 sm:h-32 bg-white/5 rounded-lg overflow-hidden mb-2">
                      <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: `${week.rate}%` }}
                        transition={{ duration: 0.8, delay: 0.8 + index * 0.1 }}
                        className={`absolute bottom-0 left-0 right-0 bg-gradient-to-t ${
                          week.rate >= 70
                            ? 'from-emerald-500/80 to-emerald-400/60'
                            : week.rate >= 40
                            ? 'from-amber-500/80 to-amber-400/60'
                            : 'from-red-500/60 to-red-400/40'
                        }`}
                      />
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-white font-bold text-lg sm:text-xl">
                          {week.rate}%
                        </span>
                      </div>
                    </div>
                    <p className="text-white/60 text-xs sm:text-sm">{week.week}</p>
                    <p className="text-white/40 text-[10px] sm:text-xs">
                      {week.complete}/{week.total} days
                    </p>
                  </motion.div>
                ))}
              </div>
            </GlassCard>
          </motion.div>

          {/* Group Members */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            <GlassCard>
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Users className="w-5 h-5 text-purple-400" />
                Group Members ({members.length})
              </h3>
              <div className="space-y-3">
                {members.map((member, index) => (
                  <motion.div
                    key={member.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.8 + index * 0.05 }}
                    className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-all"
                  >
                    <div className="flex items-center gap-3">
                      <div className="relative">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-semibold">
                          {member.name.charAt(0).toUpperCase()}
                        </div>
                        {index === 0 && (
                          <div className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center">
                            <Crown className="w-3 h-3 text-white" />
                          </div>
                        )}
                      </div>
                      <div>
                        <p className="text-white font-medium">{member.name}</p>
                        <p className="text-white/40 text-xs">{member.email}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="hidden sm:flex">
                        {index < 3 && (
                          <Badge
                            variant={index === 0 ? 'success' : index === 1 ? 'warning' : 'default'}
                          >
                            {index === 0 ? (
                              <Crown className="w-3 h-3 mr-1" />
                            ) : index === 1 ? (
                              <Medal className="w-3 h-3 mr-1" />
                            ) : (
                              <Award className="w-3 h-3 mr-1" />
                            )}
                            #{index + 1}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </GlassCard>
          </motion.div>
        </>
      )}

      {/* Health Tab Content */}
      {activeTab === 'health' && (
        <>
          {/* Period Selector and Member Filter */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between"
          >
            <div className="flex gap-2 p-1 rounded-xl bg-white/5 border border-white/10 w-fit">
              {(['week', 'month', 'year'] as const).map((period) => (
                <button
                  key={period}
                  onClick={() => setHealthPeriod(period)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all capitalize ${
                    healthPeriod === period
                      ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg'
                      : 'text-white/60 hover:text-white hover:bg-white/10'
                  }`}
                >
                  {period === 'week' ? 'This Week' : period === 'month' ? 'This Month' : 'This Year'}
                </button>
              ))}
            </div>

            {/* Member Selector - Only for Group Owners */}
            {selectedGroup && groups.find(g => g.id === selectedGroup)?.is_owner && (
              <div className="w-full sm:w-56">
                <SelectField
                  label="View Data For"
                  options={[
                    { value: '', label: 'All Members (Group)' },
                    ...members.map(m => ({ value: m.user_id, label: m.name }))
                  ]}
                  value={selectedMemberId === null ? '' : selectedMemberId}
                  onChange={(e) => setSelectedMemberId(e.target.value === '' ? null : Number(e.target.value))}
                  icon={Users}
                />
              </div>
            )}
          </motion.div>

          {healthLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 rounded-full border-2 border-emerald-500/30 border-t-emerald-500 animate-spin" />
            </div>
          ) : healthAnalytics ? (
            <>
              {/* Health Summary Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 mb-8">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                >
                  <GlassCard className="text-center py-4 sm:py-6">
                    <div className="w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-2 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center shadow-lg shadow-orange-500/30">
                      <Flame className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                    </div>
                    <p className="text-2xl sm:text-3xl font-bold text-white">
                      {healthAnalytics.summary.total_calories.toLocaleString()}
                    </p>
                    <p className="text-white/50 text-xs sm:text-sm">Calories Burned</p>
                  </GlassCard>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  <GlassCard className="text-center py-4 sm:py-6">
                    <div className="w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-2 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/30">
                      <Clock className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                    </div>
                    <p className="text-2xl sm:text-3xl font-bold text-white">
                      {formatDuration(healthAnalytics.summary.total_duration_minutes)}
                    </p>
                    <p className="text-white/50 text-xs sm:text-sm">Active Time</p>
                  </GlassCard>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  <GlassCard className="text-center py-4 sm:py-6">
                    <div className="w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-2 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/30">
                      <Activity className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                    </div>
                    <p className="text-2xl sm:text-3xl font-bold text-white">
                      {healthAnalytics.summary.total_activities}
                    </p>
                    <p className="text-white/50 text-xs sm:text-sm">Activities</p>
                  </GlassCard>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  <GlassCard className="text-center py-4 sm:py-6">
                    <div className="w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-2 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/30">
                      <Calendar className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                    </div>
                    <p className="text-2xl sm:text-3xl font-bold text-white">
                      {healthAnalytics.summary.active_days}
                    </p>
                    <p className="text-white/50 text-xs sm:text-sm">Active Days</p>
                  </GlassCard>
                </motion.div>
              </div>

              {/* Daily Calorie Trend */}
              {healthAnalytics.daily_trend.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="mb-8"
                >
                  <GlassCard>
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-emerald-400" />
                      Daily Calorie Trend
                    </h3>
                    <div className="space-y-4">
                      <div className="flex items-end justify-center gap-1 sm:gap-2 h-48 pb-10 relative">
                        {healthAnalytics.daily_trend.map((day, index) => {
                          const maxCalories = Math.max(...healthAnalytics.daily_trend.map(d => d.calories))
                          const heightPercent = maxCalories > 0 ? (day.calories / maxCalories) * 100 : 0
                          const date = new Date(day.date)
                          const monthAbbrev = date.toLocaleDateString('en-US', { month: 'short' })
                          const dayNum = date.getDate()
                          const dateLabel = `${monthAbbrev}-${dayNum}`

                          return (
                            <div
                              key={day.date}
                              className="flex-1 min-w-[25px] max-w-[50px] h-full relative group"
                            >
                              {/* Animated Bar */}
                              <motion.div
                                initial={{ scaleY: 0 }}
                                animate={{ scaleY: heightPercent > 0 ? heightPercent / 100 : 0.05 }}
                                transition={{ delay: 0.6 + index * 0.02, duration: 0.4 }}
                                style={{ transformOrigin: 'bottom', height: '100%' }}
                                className={`w-full rounded-t-md transition-all cursor-pointer ${
                                  day.calories > 0
                                    ? 'bg-gradient-to-t from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 shadow-lg hover:shadow-emerald-500/50'
                                    : 'bg-white/10'
                                }`}
                              >
                                {/* Hover Tooltip */}
                                {day.calories > 0 && (
                                  <div className="absolute -top-14 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-20">
                                    <div className="relative bg-gradient-to-r from-orange-500 to-red-500 text-white text-xs px-3 py-2 rounded-lg shadow-xl whitespace-nowrap">
                                      <div className="flex items-center gap-2">
                                        <Flame className="w-4 h-4 animate-pulse" />
                                        <span className="font-semibold">{day.calories} cal</span>
                                      </div>
                                      {/* Tooltip arrow */}
                                      <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-red-500 rotate-45" />
                                    </div>
                                  </div>
                                )}
                              </motion.div>

                              {/* Date Label */}
                              <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 text-[9px] sm:text-[10px] text-white/50 whitespace-nowrap">
                                {dateLabel}
                              </div>
                            </div>
                          )
                        })}
                      </div>
                      <div className="text-center text-white/30 text-xs italic">
                        {healthPeriod === 'week' && 'Past 7 Days'}
                        {healthPeriod === 'month' && 'Past 30 Days'}
                        {healthPeriod === 'year' && 'Past 365 Days'}
                      </div>
                    </div>
                  </GlassCard>
                </motion.div>
              )}

              {/* Activity Breakdown */}
              {healthAnalytics.activity_breakdown.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  className="mb-8"
                >
                  <GlassCard>
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                      <Dumbbell className="w-5 h-5 text-emerald-400" />
                      Top Activities
                    </h3>
                    <div className="space-y-3">
                      {healthAnalytics.activity_breakdown.slice(0, 5).map((item, index) => {
                        const colorClasses = getColorClasses(item.activity_type.color)
                        return (
                          <motion.div
                            key={item.activity_type.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.7 + index * 0.05 }}
                            className="flex items-center gap-3"
                          >
                            <ActivityIcon
                              icon={item.activity_type.icon}
                              color={item.activity_type.color}
                              size="sm"
                            />
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-white font-medium truncate">
                                  {item.activity_type.name}
                                </span>
                                <div className="flex items-center gap-2 text-sm">
                                  <span className="text-white/60">{item.count}x</span>
                                  <span className={colorClasses.text}>{item.calories} cal</span>
                                </div>
                              </div>
                              <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                                <motion.div
                                  initial={{ width: 0 }}
                                  animate={{ width: `${item.percentage}%` }}
                                  transition={{ delay: 0.8 + index * 0.05, duration: 0.5 }}
                                  className={`h-full ${colorClasses.bg} rounded-full`}
                                />
                              </div>
                            </div>
                          </motion.div>
                        )
                      })}
                    </div>
                  </GlassCard>
                </motion.div>
              )}

              {/* Category Breakdown */}
              {healthAnalytics.category_breakdown.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.7 }}
                >
                  <GlassCard>
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                      <Target className="w-5 h-5 text-emerald-400" />
                      Category Breakdown
                    </h3>
                    <div className="grid gap-3 sm:grid-cols-2">
                      {healthAnalytics.category_breakdown.map((cat, index) => {
                        const totalCalories = healthAnalytics.category_breakdown.reduce((sum, c) => sum + c.calories, 0)
                        const percentage = totalCalories > 0 ? Math.round((cat.calories / totalCalories) * 100) : 0
                        const gradient = categoryColors[cat.category] || 'from-gray-500 to-gray-400'
                        return (
                          <motion.div
                            key={cat.category}
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.8 + index * 0.05 }}
                            className="p-3 rounded-xl bg-white/5 border border-white/10"
                          >
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-white/80 text-sm">
                                {categoryLabels[cat.category] || cat.category}
                              </span>
                              <span className="text-white font-semibold text-sm">{percentage}%</span>
                            </div>
                            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${percentage}%` }}
                                transition={{ delay: 0.9 + index * 0.05, duration: 0.5 }}
                                className={`h-full bg-gradient-to-r ${gradient} rounded-full`}
                              />
                            </div>
                            <div className="flex items-center justify-between mt-2 text-xs text-white/50">
                              <span>{cat.count} activities</span>
                              <span>{cat.calories} calories</span>
                            </div>
                          </motion.div>
                        )
                      })}
                    </div>
                  </GlassCard>
                </motion.div>
              )}
            </>
          ) : (
            <EmptyState
              icon={Heart}
              title="No Health Data"
              description="Log some activities to see your health analytics"
            />
          )}
        </>
      )}
    </PageContainer>
  )
}

import { useState, useEffect } from 'react'
import { api } from '../api'
import { motion } from 'framer-motion'
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
  ChevronRight
} from 'lucide-react'
import {
  GlassCard,
  SelectField,
  PageContainer,
  PageTitle,
  EmptyState,
  Badge
} from '../components/ui'

type Group = { id: number; name: string }
type Member = { id: number; user_id: number; name: string; email: string }
type HistoryDay = { date: string; completed_sections: string[]; is_complete: boolean }

export default function Analytics() {
  const [groups, setGroups] = useState<Group[]>([])
  const [selectedGroup, setSelectedGroup] = useState<number | null>(null)
  const [members, setMembers] = useState<Member[]>([])
  const [history, setHistory] = useState<HistoryDay[]>([])
  const [streak, setStreak] = useState(0)
  const [loading, setLoading] = useState(true)

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

  return (
    <PageContainer>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
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
    </PageContainer>
  )
}

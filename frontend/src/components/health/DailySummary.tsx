import { motion } from 'framer-motion'
import { Clock, Flame, Activity } from 'lucide-react'

interface DailySummaryProps {
  summary: {
    total_duration_minutes: number
    total_calories: number
    activity_count: number
  }
}

export function DailySummary({ summary }: DailySummaryProps) {
  const formatDuration = (minutes: number) => {
    if (minutes === 0) return '0m'
    if (minutes < 60) return `${minutes}m`
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
  }

  const stats = [
    {
      icon: Clock,
      value: formatDuration(summary.total_duration_minutes),
      label: 'Total Time',
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/20',
      borderColor: 'border-blue-500/30'
    },
    {
      icon: Flame,
      value: summary.total_calories.toLocaleString(),
      label: 'Calories',
      color: 'text-orange-400',
      bgColor: 'bg-orange-500/20',
      borderColor: 'border-orange-500/30'
    },
    {
      icon: Activity,
      value: summary.activity_count,
      label: 'Activities',
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/20',
      borderColor: 'border-emerald-500/30'
    }
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="grid grid-cols-3 gap-3 p-4 rounded-xl bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-cyan-500/10 border border-emerald-500/20"
    >
      {stats.map((stat, index) => {
        const Icon = stat.icon
        return (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className="flex flex-col items-center text-center"
          >
            <div className={`
              w-10 h-10 rounded-xl ${stat.bgColor} border ${stat.borderColor}
              flex items-center justify-center mb-2
            `}>
              <Icon className={`w-5 h-5 ${stat.color}`} />
            </div>
            <motion.span
              key={String(stat.value)}
              initial={{ scale: 1.2 }}
              animate={{ scale: 1 }}
              className="text-xl font-bold text-white"
            >
              {stat.value}
            </motion.span>
            <span className="text-xs text-white/50 mt-0.5">{stat.label}</span>
          </motion.div>
        )
      })}
    </motion.div>
  )
}

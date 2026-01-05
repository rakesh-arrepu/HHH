import {
  Activity,
  Bike,
  Brain,
  Baby,
  Circle,
  CircleDot,
  Dog,
  Dumbbell,
  Flag,
  Flame,
  Flower,
  Footprints,
  Goal,
  Home,
  Mountain,
  Move,
  Music,
  Repeat,
  Shield,
  Ship,
  Snowflake,
  Sparkles,
  Square,
  Swords,
  Target,
  TrendingUp,
  User,
  Waves,
  Wind,
  X,
  Zap,
  type LucideIcon
} from 'lucide-react'

// Map icon names to Lucide components
const ICON_MAP: Record<string, LucideIcon> = {
  'activity': Activity,
  'bike': Bike,
  'brain': Brain,
  'baby': Baby,
  'circle': Circle,
  'circle-dot': CircleDot,
  'dog': Dog,
  'dumbbell': Dumbbell,
  'flag': Flag,
  'flame': Flame,
  'flower': Flower,
  'footprints': Footprints,
  'goal': Goal,
  'home': Home,
  'mountain': Mountain,
  'move': Move,
  'music': Music,
  'repeat': Repeat,
  'shield': Shield,
  'ship': Ship,
  'snowflake': Snowflake,
  'sparkles': Sparkles,
  'square': Square,
  'swords': Swords,
  'target': Target,
  'trending-up': TrendingUp,
  'user': User,
  'waves': Waves,
  'wind': Wind,
  'x': X,
  'zap': Zap,
}

// Map color names to Tailwind classes
const COLOR_MAP: Record<string, { bg: string; text: string; border: string; glow: string }> = {
  emerald: { bg: 'bg-emerald-500', text: 'text-emerald-400', border: 'border-emerald-500/30', glow: 'shadow-emerald-500/30' },
  red: { bg: 'bg-red-500', text: 'text-red-400', border: 'border-red-500/30', glow: 'shadow-red-500/30' },
  orange: { bg: 'bg-orange-500', text: 'text-orange-400', border: 'border-orange-500/30', glow: 'shadow-orange-500/30' },
  blue: { bg: 'bg-blue-500', text: 'text-blue-400', border: 'border-blue-500/30', glow: 'shadow-blue-500/30' },
  cyan: { bg: 'bg-cyan-500', text: 'text-cyan-400', border: 'border-cyan-500/30', glow: 'shadow-cyan-500/30' },
  pink: { bg: 'bg-pink-500', text: 'text-pink-400', border: 'border-pink-500/30', glow: 'shadow-pink-500/30' },
  purple: { bg: 'bg-purple-500', text: 'text-purple-400', border: 'border-purple-500/30', glow: 'shadow-purple-500/30' },
  teal: { bg: 'bg-teal-500', text: 'text-teal-400', border: 'border-teal-500/30', glow: 'shadow-teal-500/30' },
  indigo: { bg: 'bg-indigo-500', text: 'text-indigo-400', border: 'border-indigo-500/30', glow: 'shadow-indigo-500/30' },
  fuchsia: { bg: 'bg-fuchsia-500', text: 'text-fuchsia-400', border: 'border-fuchsia-500/30', glow: 'shadow-fuchsia-500/30' },
  yellow: { bg: 'bg-yellow-500', text: 'text-yellow-400', border: 'border-yellow-500/30', glow: 'shadow-yellow-500/30' },
  lime: { bg: 'bg-lime-500', text: 'text-lime-400', border: 'border-lime-500/30', glow: 'shadow-lime-500/30' },
  green: { bg: 'bg-green-500', text: 'text-green-400', border: 'border-green-500/30', glow: 'shadow-green-500/30' },
  amber: { bg: 'bg-amber-500', text: 'text-amber-400', border: 'border-amber-500/30', glow: 'shadow-amber-500/30' },
  violet: { bg: 'bg-violet-500', text: 'text-violet-400', border: 'border-violet-500/30', glow: 'shadow-violet-500/30' },
  sky: { bg: 'bg-sky-500', text: 'text-sky-400', border: 'border-sky-500/30', glow: 'shadow-sky-500/30' },
  gray: { bg: 'bg-gray-500', text: 'text-gray-400', border: 'border-gray-500/30', glow: 'shadow-gray-500/30' },
  slate: { bg: 'bg-slate-500', text: 'text-slate-400', border: 'border-slate-500/30', glow: 'shadow-slate-500/30' },
  stone: { bg: 'bg-stone-500', text: 'text-stone-400', border: 'border-stone-500/30', glow: 'shadow-stone-500/30' },
  white: { bg: 'bg-white', text: 'text-white', border: 'border-white/30', glow: 'shadow-white/30' },
}

interface ActivityIconProps {
  icon: string
  color?: string
  size?: 'sm' | 'md' | 'lg'
  variant?: 'filled' | 'outline' | 'ghost'
  className?: string
}

export function ActivityIcon({
  icon,
  color = 'emerald',
  size = 'md',
  variant = 'filled',
  className = ''
}: ActivityIconProps) {
  const IconComponent = ICON_MAP[icon] || Activity
  const colorClasses = COLOR_MAP[color] || COLOR_MAP.gray

  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12'
  }

  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  }

  if (variant === 'ghost') {
    return (
      <div className={`${sizeClasses[size]} rounded-xl flex items-center justify-center ${className}`}>
        <IconComponent className={`${iconSizes[size]} ${colorClasses.text}`} />
      </div>
    )
  }

  if (variant === 'outline') {
    return (
      <div className={`${sizeClasses[size]} rounded-xl border-2 ${colorClasses.border} flex items-center justify-center bg-white/5 ${className}`}>
        <IconComponent className={`${iconSizes[size]} ${colorClasses.text}`} />
      </div>
    )
  }

  return (
    <div className={`${sizeClasses[size]} rounded-xl ${colorClasses.bg} flex items-center justify-center shadow-lg ${colorClasses.glow} ${className}`}>
      <IconComponent className={`${iconSizes[size]} text-white`} />
    </div>
  )
}

export function getColorClasses(color: string) {
  return COLOR_MAP[color] || COLOR_MAP.gray
}

// Health Activity Types for the revamped Health section

export interface ActivityType {
  id: number
  name: string
  category: 'cardio' | 'sports' | 'strength' | 'mind_body' | 'outdoor' | 'home'
  icon: string // Lucide icon name
  color: string // Tailwind color
  met_value: number
  default_duration: number
}

export interface ActivityTypeGrouped {
  category: string
  activities: ActivityType[]
}

export interface HealthActivity {
  id: number
  activity_type: ActivityType
  duration: number | null
  duration_unit: 'minutes' | 'hours'
  distance: number | null
  calories: number
  notes: string | null
  created_at: string
}

export interface DailyHealthSummary {
  date: string
  activities: HealthActivity[]
  summary: {
    total_duration_minutes: number
    total_calories: number
    activity_count: number
  }
  legacy_content: string | null
}

export interface NewHealthActivity {
  group_id: number
  activity_type_id: number
  entry_date?: string
  duration?: number
  duration_unit?: 'minutes' | 'hours'
  distance?: number
  notes?: string
}

export interface UpdateHealthActivity {
  duration?: number
  duration_unit?: 'minutes' | 'hours'
  distance?: number
  notes?: string
}

export interface QuickLogRequest {
  group_id: number
  activity_type_id: number
  entry_date?: string
}

export interface ActivityFavorite {
  id: number
  activity_type: ActivityType
  display_order: number
}

export interface HealthAnalytics {
  period: 'week' | 'month' | 'year'
  summary: {
    total_activities: number
    total_duration_minutes: number
    total_calories: number
    active_days: number
  }
  activity_breakdown: Array<{
    activity_type: ActivityType
    count: number
    duration: number
    calories: number
    percentage: number
  }>
  daily_trend: Array<{
    date: string
    calories: number
    duration_minutes: number
    activities: number
  }>
  category_breakdown: Array<{
    category: string
    count: number
    calories: number
  }>
}

// Category display names and colors
export const CATEGORY_LABELS: Record<string, string> = {
  cardio: 'Cardio',
  sports: 'Sports',
  strength: 'Strength & Fitness',
  mind_body: 'Mind & Body',
  outdoor: 'Outdoor & Adventure',
  home: 'Home & Daily'
}

export const CATEGORY_COLORS: Record<string, string> = {
  cardio: 'emerald',
  sports: 'yellow',
  strength: 'purple',
  mind_body: 'violet',
  outdoor: 'green',
  home: 'indigo'
}

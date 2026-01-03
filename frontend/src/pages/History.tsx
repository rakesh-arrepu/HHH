import { useState, useEffect } from 'react'
import { api } from '../api'

type Group = { id: number; name: string }
type HistoryDay = { date: string; completed_sections: string[]; is_complete: boolean }

export default function History() {
  const [groups, setGroups] = useState<Group[]>([])
  const [selectedGroup, setSelectedGroup] = useState<number | null>(null)
  const [history, setHistory] = useState<HistoryDay[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadGroups()
  }, [])

  useEffect(() => {
    if (selectedGroup) {
      loadHistory()
    }
  }, [selectedGroup])

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
    try {
      const data = await api.getHistory(selectedGroup, 30)
      setHistory(data)
    } catch (err) {
      console.error('Failed to load history:', err)
    }
  }

  if (loading) {
    return <div className="text-center text-gray-500">Loading...</div>
  }

  if (groups.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No groups found. Create a group first.</p>
      </div>
    )
  }

  // Calculate stats
  const completeDays = history.filter((d) => d.is_complete).length
  const partialDays = history.filter((d) => d.completed_sections.length > 0 && !d.is_complete).length

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">History</h1>
        <select
          value={selectedGroup || ''}
          onChange={(e) => setSelectedGroup(Number(e.target.value))}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          {groups.map((g) => (
            <option key={g.id} value={g.id}>
              {g.name}
            </option>
          ))}
        </select>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-white p-4 rounded-lg border text-center">
          <div className="text-3xl font-bold text-green-600">{completeDays}</div>
          <div className="text-sm text-gray-500">Complete Days</div>
        </div>
        <div className="bg-white p-4 rounded-lg border text-center">
          <div className="text-3xl font-bold text-yellow-600">{partialDays}</div>
          <div className="text-sm text-gray-500">Partial Days</div>
        </div>
        <div className="bg-white p-4 rounded-lg border text-center">
          <div className="text-3xl font-bold text-indigo-600">
            {Math.round((completeDays / 30) * 100)}%
          </div>
          <div className="text-sm text-gray-500">Completion Rate</div>
        </div>
      </div>

      {/* Calendar grid */}
      <div className="bg-white rounded-lg border p-6">
        <h2 className="text-lg font-semibold mb-4">Last 30 Days</h2>
        <div className="grid grid-cols-7 gap-2">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
            <div key={day} className="text-center text-xs text-gray-500 font-medium py-2">
              {day}
            </div>
          ))}

          {/* Add empty cells for alignment */}
          {history.length > 0 &&
            Array.from({ length: new Date(history[history.length - 1].date).getDay() }).map(
              (_, i) => <div key={`empty-${i}`} />
            )}

          {[...history].reverse().map((day) => {
            const date = new Date(day.date)
            const isToday = day.date === new Date().toISOString().split('T')[0]

            let bgColor = 'bg-gray-100'
            if (day.is_complete) {
              bgColor = 'bg-green-500'
            } else if (day.completed_sections.length === 2) {
              bgColor = 'bg-yellow-400'
            } else if (day.completed_sections.length === 1) {
              bgColor = 'bg-yellow-200'
            }

            return (
              <div
                key={day.date}
                className={`aspect-square rounded-md flex items-center justify-center text-sm ${bgColor} ${
                  isToday ? 'ring-2 ring-indigo-500' : ''
                } ${day.is_complete ? 'text-white' : 'text-gray-700'}`}
                title={`${day.date}: ${day.completed_sections.join(', ') || 'No entries'}`}
              >
                {date.getDate()}
              </div>
            )
          })}
        </div>

        {/* Legend */}
        <div className="flex justify-center gap-6 mt-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-green-500" />
            <span className="text-gray-600">Complete (3/3)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-yellow-400" />
            <span className="text-gray-600">Partial</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-gray-100" />
            <span className="text-gray-600">No entries</span>
          </div>
        </div>
      </div>
    </div>
  )
}

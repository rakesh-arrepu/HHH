import React from 'react'

export default function CalendarView() {
  // Mock data - last 7 days with entry status
  const days = [
    { date: '2025-11-03', hasEntry: true },
    { date: '2025-11-04', hasEntry: true },
    { date: '2025-11-05', hasEntry: false },
    { date: '2025-11-06', hasEntry: true },
    { date: '2025-11-07', hasEntry: true },
    { date: '2025-11-08', hasEntry: true },
    { date: '2025-11-09', hasEntry: true },
  ]

  return (
    <div className="space-y-2">
      <div className="text-sm text-gray-600 mb-3">Last 7 days</div>
      <div className="grid grid-cols-7 gap-1">
        {days.map((day, index) => (
          <div
            key={day.date}
            className={`aspect-square rounded-md flex items-center justify-center text-xs font-medium ${
              day.hasEntry
                ? 'bg-green-500 text-white'
                : 'bg-gray-200 text-gray-400'
            }`}
            title={day.hasEntry ? 'Entry completed' : 'No entry'}
          >
            {new Date(day.date).getDate()}
          </div>
        ))}
      </div>
      <div className="flex items-center justify-center space-x-4 text-xs text-gray-500 mt-3">
        <div className="flex items-center space-x-1">
          <div className="w-3 h-3 bg-green-500 rounded"></div>
          <span>Completed</span>
        </div>
        <div className="flex items-center space-x-1">
          <div className="w-3 h-3 bg-gray-200 rounded"></div>
          <span>Missed</span>
        </div>
      </div>
    </div>
  )
}

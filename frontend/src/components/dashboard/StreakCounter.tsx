import React from 'react'

export default function StreakCounter() {
  const currentStreak = 7 // Mock data
  const longestStreak = 15 // Mock data

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Streak Counter</h3>
      <div className="text-center">
        <div className="text-6xl font-bold text-orange-500 mb-2">🔥</div>
        <div className="text-4xl font-bold text-orange-600 mb-1">{currentStreak}</div>
        <div className="text-sm text-gray-600 mb-4">days in a row</div>
        <div className="text-xs text-gray-500">
          Personal best: {longestStreak} days
        </div>
      </div>
    </div>
  )
}

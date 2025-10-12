import React from 'react'

export default function Analytics() {
  // Mock data - will be replaced with real data from API
  const stats = {
    totalEntries: 42,
    currentStreak: 7,
    longestStreak: 15,
    completionRate: 78
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Analytics Overview</h3>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Total Entries</span>
          <span className="text-2xl font-bold text-blue-600">{stats.totalEntries}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Current Streak</span>
          <span className="text-2xl font-bold text-green-600">{stats.currentStreak} days</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Longest Streak</span>
          <span className="text-2xl font-bold text-purple-600">{stats.longestStreak} days</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Completion Rate</span>
          <span className="text-2xl font-bold text-orange-600">{stats.completionRate}%</span>
        </div>
      </div>
    </div>
  )
}

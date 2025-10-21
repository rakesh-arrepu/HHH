import React from 'react'
import { gql } from '@apollo/client'
import { useQuery } from '@apollo/client/react'
import Analytics from '../components/dashboard/Analytics'
import StreakCounter from '../components/dashboard/StreakCounter'
import ProgressBar from '../components/dashboard/ProgressBar'
import EntryForm from '../components/entries/EntryForm'
import CalendarView from '../components/entries/CalendarView'

const HEALTH_QUERY = gql`
  query Health {
    health
  }
`

export default function Dashboard() {
  const { data, loading, error } = useQuery<{ health: string }>(HEALTH_QUERY)
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Daily Tracker Dashboard</h1>
        <p className="mt-2 text-gray-600">Track your daily progress and maintain your streaks</p>
      </div>

      <div className="bg-white p-4 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-2">API Status</h2>
        {loading && <p className="text-gray-600">Checking GraphQL…</p>}
        {error && <p className="text-red-600">GraphQL error: {error.message}</p>}
        {!loading && !error && (
          <p className="text-green-700">GraphQL health: {data?.health ?? 'unknown'}</p>
        )}
      </div>

      {/* Analytics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Analytics />
        <StreakCounter />
        <ProgressBar />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Entry Form */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Add Today's Entry</h2>
          <EntryForm />
        </div>

        {/* Calendar View */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Your Progress Calendar</h2>
          <CalendarView />
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="flex flex-wrap gap-4">
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            Create Entry
          </button>
          <button className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700">
            View Groups
          </button>
          <button className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700">
            Settings
          </button>
        </div>
      </div>
    </div>
  )
}

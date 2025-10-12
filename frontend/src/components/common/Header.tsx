import React from 'react'
import { Link, useNavigate } from 'react-router-dom'

export default function Header() {
  const navigate = useNavigate()

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="text-xl font-bold text-blue-600">
              Daily Tracker
            </Link>
            <nav className="hidden md:flex space-x-6">
              <Link to="/dashboard" className="text-gray-700 hover:text-blue-600">
                Dashboard
              </Link>
              <Link to="/groups" className="text-gray-700 hover:text-blue-600">
                Groups
              </Link>
              <Link to="/profile" className="text-gray-700 hover:text-blue-600">
                Profile
              </Link>
            </nav>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/login')}
              className="text-gray-700 hover:text-blue-600"
            >
              Login
            </button>
            <button
              onClick={() => navigate('/register')}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Sign Up
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

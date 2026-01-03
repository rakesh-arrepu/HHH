import React from 'react'
import { HashRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Groups from './pages/Groups'
import Profile from './pages/Profile'
import Admin from './pages/Admin'
import LoginForm from './components/auth/LoginForm'
import RegisterForm from './components/auth/RegisterForm'
import TwoFactorSetup from './components/auth/TwoFactorSetup'
import Header from './components/common/Header'
import ErrorBoundary from './components/common/ErrorBoundary'

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <a href="#main-content" className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:bg-white focus:text-blue-700 focus:ring-2 focus:ring-blue-500 px-3 py-2 rounded">
            Skip to main content
          </a>
          <Header />
          <main id="main-content" role="main" className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/groups" element={<Groups />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/admin" element={<Admin />} />
              <Route path="/login" element={<LoginForm />} />
              <Route path="/register" element={<RegisterForm />} />
              <Route path="/2fa-setup" element={<TwoFactorSetup />} />
              <Route
                path="*"
                element={
                  <div className="flex flex-col items-center mt-20">
                    <span className="text-4xl font-bold text-red-600 mb-4">404</span>
                    <span className="text-lg font-semibold mb-2">Page Not Found</span>
                    <span className="text-gray-600">The page you are looking for does not exist.</span>
                  </div>
                }
              />
            </Routes>
          </main>
        </div>
      </Router>
    </ErrorBoundary>
  )
}

export default App

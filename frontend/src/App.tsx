import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Groups from './pages/Groups'
import Profile from './pages/Profile'
import Admin from './pages/Admin'
import LoginForm from './components/auth/LoginForm'
import RegisterForm from './components/auth/RegisterForm'
import SignUp from './pages/SignUp'
import Header from './components/common/Header'
import ErrorBoundary from './components/common/ErrorBoundary'

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Header />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/groups" element={<Groups />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/admin" element={<Admin />} />
              <Route path="/login" element={<LoginForm />} />
              <Route path="/register" element={<RegisterForm />} />
              <Route path="/signup" element={<SignUp />} />
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

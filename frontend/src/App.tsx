import { useEffect } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'

// Layout components
import AuthLayout from './components/AuthLayout'
import Layout from './components/Layout'

// Pages
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import Dashboard from './pages/Dashboard'

function App() {
  const { user, isLoading, initializeAuth } = useAuthStore()

  useEffect(() => {
    initializeAuth()
  }, [initializeAuth])

  if (isLoading) {
    return (
      <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-3" style={{width: '2rem', height: '2rem'}}></div>
          <p className="text-muted">Loading AI Educational Platform...</p>
        </div>
      </div>
    )
  }

  // Protected route wrapper
  const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    if (!user) {
      return <Navigate to="/login" replace />
    }
    return <>{children}</>
  }

  return (
    <div className="App">
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={
          user ? <Navigate to="/dashboard" replace /> : (
            <AuthLayout>
              <Login />
            </AuthLayout>
          )
        } />
        
        <Route path="/register" element={
          user ? <Navigate to="/dashboard" replace /> : (
            <AuthLayout>
              <Register />
            </AuthLayout>
          )
        } />

        {/* Protected routes */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout>
              <Navigate to="/dashboard" replace />
            </Layout>
          </ProtectedRoute>
        } />

        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </ProtectedRoute>
        } />

        {/* 404 fallback */}
        <Route path="*" element={
          <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
            <div className="text-center">
              <h1 className="display-1 fw-bold text-primary mb-4">404</h1>
              <p className="text-muted fs-5 mb-4">Page not found</p>
              <button 
                onClick={() => window.history.back()}
                className="btn btn-primary btn-lg"
              >
                <i className="bi bi-arrow-left me-2"></i>
                Go Back
              </button>
            </div>
          </div>
        } />
      </Routes>
    </div>
  )
}

export default App
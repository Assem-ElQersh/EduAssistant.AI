import React, { useState } from 'react'
import { Alert, Button, FloatingLabel, Form } from 'react-bootstrap'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'

const Login: React.FC = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login, isLoading } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <>
      <div className="text-center mb-4">
        <h2 className="h4 fw-bold text-dark">Welcome Back!</h2>
        <p className="text-muted">Sign in to continue your Japanese learning journey</p>
      </div>

      {error && (
        <Alert variant="danger" className="d-flex align-items-center">
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          {error}
        </Alert>
      )}

      <Form onSubmit={handleSubmit}>
        <div className="mb-3">
          <FloatingLabel controlId="email" label="Email address">
            <Form.Control
              type="email"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="form-control-lg"
            />
          </FloatingLabel>
        </div>

        <div className="mb-4">
          <FloatingLabel controlId="password" label="Password">
            <Form.Control
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="form-control-lg"
            />
          </FloatingLabel>
        </div>

        <div className="d-grid mb-4">
          <Button
            type="submit"
            size="lg"
            className="btn-gradient-primary"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="loading-spinner me-2"></span>
                Signing in...
              </>
            ) : (
              <>
                <i className="bi bi-box-arrow-in-right me-2"></i>
                Sign In
              </>
            )}
          </Button>
        </div>
      </Form>

      <hr className="my-4" />

      <div className="text-center">
        <p className="text-muted mb-3">Don't have an account?</p>
        <div className="d-grid">
          <Button
            variant="outline-primary"
            size="lg"
            href="/register"
            className="btn-outline-gradient"
          >
            <i className="bi bi-person-plus me-2"></i>
            Create Account
          </Button>
        </div>
      </div>

      <div className="text-center mt-4">
        <small className="text-muted">
          <i className="bi bi-shield-check me-1"></i>
          Your data is secure and protected
        </small>
      </div>
    </>
  )
}

export default Login
import React, { useState } from 'react'
import { Alert, Button, Col, FloatingLabel, Form, Row } from 'react-bootstrap'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'

const Register: React.FC = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'student' as 'student' | 'teacher',
    jlpt_level: 'N5'
  })
  const [error, setError] = useState('')
  const { register, isLoading } = useAuthStore()
  const navigate = useNavigate()

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long')
      return
    }

    try {
      await register({
        full_name: formData.full_name,
        username: formData.username,
        email: formData.email,
        password: formData.password,
        role: formData.role,
        jlpt_level: formData.jlpt_level
      })
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed')
    }
  }

  return (
    <>
      <div className="text-center mb-4">
        <h2 className="h4 fw-bold text-dark">Join Our Community!</h2>
        <p className="text-muted">Start your Japanese learning journey today</p>
      </div>

      {error && (
        <Alert variant="danger" className="d-flex align-items-center">
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          {error}
        </Alert>
      )}

      <Form onSubmit={handleSubmit}>
        <Row className="g-3 mb-3">
          <Col md={6}>
            <FloatingLabel controlId="fullName" label="Full Name">
              <Form.Control
                type="text"
                placeholder="John Doe"
                value={formData.full_name}
                onChange={(e) => handleChange('full_name', e.target.value)}
                required
              />
            </FloatingLabel>
          </Col>
          <Col md={6}>
            <FloatingLabel controlId="username" label="Username">
              <Form.Control
                type="text"
                placeholder="johndoe"
                value={formData.username}
                onChange={(e) => handleChange('username', e.target.value)}
                required
              />
            </FloatingLabel>
          </Col>
        </Row>

        <div className="mb-3">
          <FloatingLabel controlId="email" label="Email address">
            <Form.Control
              type="email"
              placeholder="name@example.com"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              required
            />
          </FloatingLabel>
        </div>

        <Row className="g-3 mb-3">
          <Col md={6}>
            <FloatingLabel controlId="password" label="Password">
              <Form.Control
                type="password"
                placeholder="Password"
                value={formData.password}
                onChange={(e) => handleChange('password', e.target.value)}
                required
                minLength={6}
              />
            </FloatingLabel>
          </Col>
          <Col md={6}>
            <FloatingLabel controlId="confirmPassword" label="Confirm Password">
              <Form.Control
                type="password"
                placeholder="Confirm Password"
                value={formData.confirmPassword}
                onChange={(e) => handleChange('confirmPassword', e.target.value)}
                required
                minLength={6}
              />
            </FloatingLabel>
          </Col>
        </Row>

        <Row className="g-3 mb-4">
          <Col md={6}>
            <FloatingLabel controlId="role" label="I am a...">
              <Form.Select
                value={formData.role}
                onChange={(e) => handleChange('role', e.target.value)}
                required
              >
                <option value="student">Student</option>
                <option value="teacher">Teacher</option>
              </Form.Select>
            </FloatingLabel>
          </Col>
          <Col md={6}>
            <FloatingLabel controlId="jlptLevel" label="JLPT Level">
              <Form.Select
                value={formData.jlpt_level}
                onChange={(e) => handleChange('jlpt_level', e.target.value)}
              >
                <option value="N5">N5 (Beginner)</option>
                <option value="N4">N4 (Elementary)</option>
                <option value="N3">N3 (Intermediate)</option>
                <option value="N2">N2 (Upper Intermediate)</option>
                <option value="N1">N1 (Advanced)</option>
              </Form.Select>
            </FloatingLabel>
          </Col>
        </Row>

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
                Creating Account...
              </>
            ) : (
              <>
                <i className="bi bi-person-plus me-2"></i>
                Create Account
              </>
            )}
          </Button>
        </div>
      </Form>

      <hr className="my-4" />

      <div className="text-center">
        <p className="text-muted mb-3">Already have an account?</p>
        <div className="d-grid">
          <Button
            variant="outline-primary"
            size="lg"
            href="/login"
            className="btn-outline-gradient"
          >
            <i className="bi bi-box-arrow-in-right me-2"></i>
            Sign In
          </Button>
        </div>
      </div>

      <div className="text-center mt-4">
        <small className="text-muted">
          By creating an account, you agree to our Terms of Service and Privacy Policy
        </small>
      </div>
    </>
  )
}

export default Register
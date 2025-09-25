import React from 'react'
import { Card, Col, Container, Row } from 'react-bootstrap'
import { useAuthStore } from '../stores/authStore'

const Dashboard: React.FC = () => {
  const { user } = useAuthStore()

  return (
    <div className="bg-light min-vh-100 py-4">
      <Container fluid>
        {/* Welcome Header */}
        <Row className="mb-4">
          <Col>
            <Card className="welcome-card border-0 shadow-sm">
              <Card.Body className="py-4">
                <Row className="align-items-center">
                  <Col md={8}>
                    <div className="d-flex align-items-center mb-2">
                      <h1 className="display-6 fw-bold text-primary mb-0 me-3">
                        Welcome back, {user?.full_name || user?.username || 'Student'}!
                      </h1>
                      <span className="fs-2">🎌</span>
                    </div>
                    <p className="text-muted fs-5 mb-0">
                      Ready to continue your Japanese learning journey?
                    </p>
                  </Col>
                  <Col md={4} className="text-md-end">
                    <div className="d-flex flex-wrap justify-content-md-end gap-3">
                      {user?.jlpt_level && (
                        <span className="jlpt-badge">
                          JLPT {user.jlpt_level}
                        </span>
                      )}
                      <span className="study-streak-badge">
                        <i className="bi bi-fire"></i>
                        {user?.study_streak || 0} day streak
                      </span>
                    </div>
                  </Col>
                </Row>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Quick Stats */}
        <Row className="g-4 mb-4">
          <Col lg={3} md={6}>
            <Card className="stat-card h-100 shadow-sm border-0">
              <Card.Body>
                <div className="d-flex align-items-center">
                  <div className="stat-icon bg-primary bg-opacity-10 text-primary">
                    <i className="bi bi-clock-history"></i>
                  </div>
                  <div>
                    <h6 className="text-muted mb-1 fw-medium">Study Time</h6>
                    <h3 className="mb-0 fw-bold">0m</h3>
                    <small className="text-muted">This week</small>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>

          <Col lg={3} md={6}>
            <Card className="stat-card h-100 shadow-sm border-0">
              <Card.Body>
                <div className="d-flex align-items-center">
                  <div className="stat-icon bg-success bg-opacity-10 text-success">
                    <i className="bi bi-trophy"></i>
                  </div>
                  <div>
                    <h6 className="text-muted mb-1 fw-medium">Avg Score</h6>
                    <h3 className="mb-0 fw-bold">0%</h3>
                    <small className="text-muted">Quiz average</small>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>

          <Col lg={3} md={6}>
            <Card className="stat-card h-100 shadow-sm border-0">
              <Card.Body>
                <div className="d-flex align-items-center">
                  <div className="stat-icon bg-info bg-opacity-10 text-info">
                    <i className="bi bi-book"></i>
                  </div>
                  <div>
                    <h6 className="text-muted mb-1 fw-medium">Courses</h6>
                    <h3 className="mb-0 fw-bold">0</h3>
                    <small className="text-muted">Enrolled</small>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>

          <Col lg={3} md={6}>
            <Card className="stat-card h-100 shadow-sm border-0">
              <Card.Body>
                <div className="d-flex align-items-center">
                  <div className="stat-icon bg-warning bg-opacity-10 text-warning">
                    <i className="bi bi-lightning"></i>
                  </div>
                  <div>
                    <h6 className="text-muted mb-1 fw-medium">Sessions</h6>
                    <h3 className="mb-0 fw-bold">0</h3>
                    <small className="text-muted">This week</small>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Main Content */}
        <Row className="g-4">
          {/* Main Content Area */}
          <Col lg={8}>
            {/* Welcome Message */}
            <Card className="shadow-sm border-0 mb-4">
              <Card.Body>
                <div className="d-flex align-items-center mb-3">
                  <h2 className="h4 fw-bold text-dark mb-0 me-2">
                    Welcome to AI Educational Platform
                  </h2>
                  <span className="fs-4">🎌</span>
                </div>
                <p className="text-muted mb-4">
                  Your personalized Japanese learning journey starts here! This platform uses advanced AI 
                  to help you master Japanese language skills.
                </p>
                
                <Row className="g-3">
                  <Col md={6}>
                    <Card className="h-100 border border-primary border-opacity-25 bg-primary bg-opacity-5">
                      <Card.Body className="p-3">
                        <div className="d-flex align-items-center mb-2">
                          <i className="bi bi-robot text-primary fs-5 me-2"></i>
                          <h6 className="fw-semibold mb-0">AI Chat Assistant</h6>
                        </div>
                        <p className="small text-muted mb-0">
                          Get instant help with grammar, vocabulary, and cultural context.
                        </p>
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={6}>
                    <Card className="h-100 border border-success border-opacity-25 bg-success bg-opacity-5">
                      <Card.Body className="p-3">
                        <div className="d-flex align-items-center mb-2">
                          <i className="bi bi-graph-up text-success fs-5 me-2"></i>
                          <h6 className="fw-semibold mb-0">Progress Tracking</h6>
                        </div>
                        <p className="small text-muted mb-0">
                          Monitor your learning progress and identify areas to improve.
                        </p>
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={6}>
                    <Card className="h-100 border border-info border-opacity-25 bg-info bg-opacity-5">
                      <Card.Body className="p-3">
                        <div className="d-flex align-items-center mb-2">
                          <i className="bi bi-puzzle text-info fs-5 me-2"></i>
                          <h6 className="fw-semibold mb-0">Interactive Quizzes</h6>
                        </div>
                        <p className="small text-muted mb-0">
                          Practice with AI-generated questions tailored to your level.
                        </p>
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={6}>
                    <Card className="h-100 border border-warning border-opacity-25 bg-warning bg-opacity-5">
                      <Card.Body className="p-3">
                        <div className="d-flex align-items-center mb-2">
                          <i className="bi bi-bullseye text-warning fs-5 me-2"></i>
                          <h6 className="fw-semibold mb-0">JLPT Preparation</h6>
                        </div>
                        <p className="small text-muted mb-0">
                          Structured content from N5 to N1 levels.
                        </p>
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>
              </Card.Body>
            </Card>

            {/* Quick Actions */}
            <Card className="shadow-sm border-0">
              <Card.Body>
                <h2 className="h5 fw-bold text-dark mb-4">Quick Actions</h2>
                <Row className="g-3">
                  <Col md={4}>
                    <Card className="quick-action-card h-100">
                      <Card.Body className="text-center py-4">
                        <div className="fs-1 mb-3">💬</div>
                        <h6 className="fw-semibold text-dark">Start AI Chat</h6>
                        <p className="small text-muted mb-0">Ask questions about Japanese</p>
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={4}>
                    <Card className="quick-action-card h-100">
                      <Card.Body className="text-center py-4">
                        <div className="fs-1 mb-3">📚</div>
                        <h6 className="fw-semibold text-dark">Browse Courses</h6>
                        <p className="small text-muted mb-0">Explore learning materials</p>
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={4}>
                    <Card className="quick-action-card h-100">
                      <Card.Body className="text-center py-4">
                        <div className="fs-1 mb-3">🎯</div>
                        <h6 className="fw-semibold text-dark">Take Quiz</h6>
                        <p className="small text-muted mb-0">Test your knowledge</p>
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>
              </Card.Body>
            </Card>
          </Col>

          {/* Sidebar */}
          <Col lg={4}>
            {/* Study Streak */}
            <Card className="shadow-sm border-0 mb-4">
              <Card.Body className="text-center">
                <div className="d-flex align-items-center justify-content-center mb-3">
                  <h2 className="h5 fw-bold text-dark mb-0 me-2">Study Streak</h2>
                  <span className="fs-4">🔥</span>
                </div>
                <div className="display-4 fw-bold text-warning mb-2">
                  {user?.study_streak || 0}
                </div>
                <p className="text-muted mb-3">days in a row</p>
                <div className="p-3 rounded-3" style={{backgroundColor: 'rgba(255, 193, 7, 0.1)'}}>
                  <p className="small text-warning-emphasis mb-0">
                    {user?.study_streak && user.study_streak > 0 
                      ? "Keep it up! Consistency is key to language learning." 
                      : "Start your streak today by completing a lesson!"
                    }
                  </p>
                </div>
              </Card.Body>
            </Card>

            {/* Learning Tips */}
            <Card className="shadow-sm border-0">
              <Card.Body>
                <div className="d-flex align-items-center mb-4">
                  <h2 className="h5 fw-bold text-dark mb-0 me-2">Daily Tips</h2>
                  <span className="fs-5">💡</span>
                </div>
                
                <div className="mb-3">
                  <Card className="border-primary border-opacity-25 bg-primary bg-opacity-5">
                    <Card.Body className="p-3">
                      <div className="d-flex align-items-center mb-2">
                        <i className="bi bi-pencil text-primary me-2"></i>
                        <h6 className="fw-semibold text-primary mb-0">Hiragana Practice</h6>
                      </div>
                      <p className="small text-muted mb-0 japanese-text">
                        Practice writing hiragana characters daily. Muscle memory is crucial for Japanese writing!
                      </p>
                    </Card.Body>
                  </Card>
                </div>
                
                <div>
                  <Card className="border-success border-opacity-25 bg-success bg-opacity-5">
                    <Card.Body className="p-3">
                      <div className="d-flex align-items-center mb-2">
                        <i className="bi bi-chat-square-text text-success me-2"></i>
                        <h6 className="fw-semibold text-success mb-0">Grammar Tip</h6>
                      </div>
                      <p className="small text-muted mb-2">
                        Remember: <span className="japanese-text fw-semibold">は (wa)</span> is used as the topic particle, 
                        not <span className="japanese-text fw-semibold">を (wo)</span> which marks the object.
                      </p>
                    </Card.Body>
                  </Card>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </div>
  )
}

export default Dashboard
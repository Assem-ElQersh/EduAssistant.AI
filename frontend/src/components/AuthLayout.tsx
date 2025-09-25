import React from 'react'
import { Card, Col, Container, Row } from 'react-bootstrap'

interface AuthLayoutProps {
  children: React.ReactNode
}

const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  return (
    <div className="min-vh-100 d-flex align-items-center gradient-bg">
      <Container>
        <Row className="justify-content-center">
          <Col lg={5} md={7} sm={9}>
            <Card className="shadow-lg border-0">
              <Card.Body className="p-5">
                <div className="text-center mb-4">
                  <div className="mb-3">
                    <i className="bi bi-mortarboard-fill text-primary" style={{fontSize: '3rem'}}></i>
                  </div>
                  <h1 className="h3 fw-bold text-dark mb-2">
                    AI Educational Platform
                  </h1>
                  <p className="text-muted">
                    Your journey to Japanese fluency starts here <span className="fs-5">🎌</span>
                  </p>
                </div>
                {children}
              </Card.Body>
            </Card>
            
            {/* Decorative Elements */}
            <div className="text-center mt-4">
              <p className="text-white-50 small mb-0">
                Powered by Advanced AI • Personalized Learning • JLPT Preparation
              </p>
            </div>
          </Col>
        </Row>
      </Container>
    </div>
  )
}

export default AuthLayout
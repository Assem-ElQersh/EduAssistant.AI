import React from 'react'
import { Container, Dropdown, Nav, Navbar } from 'react-bootstrap'
import { useAuthStore } from '../stores/authStore'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuthStore()

  return (
    <div className="min-vh-100 bg-light">
      <Navbar bg="white" expand="lg" className="shadow-sm border-bottom">
        <Container fluid>
          <Navbar.Brand href="/dashboard" className="fw-bold fs-4">
            <i className="bi bi-mortarboard-fill me-2 text-primary"></i>
            AI Educational Platform
          </Navbar.Brand>
          
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link href="/dashboard" className="fw-medium">
                <i className="bi bi-house-door me-1"></i>
                Dashboard
              </Nav.Link>
              <Nav.Link href="/courses" className="fw-medium">
                <i className="bi bi-book me-1"></i>
                Courses
              </Nav.Link>
              <Nav.Link href="/assignments" className="fw-medium">
                <i className="bi bi-journal-text me-1"></i>
                Assignments
              </Nav.Link>
              <Nav.Link href="/chat" className="fw-medium">
                <i className="bi bi-chat-dots me-1"></i>
                AI Chat
              </Nav.Link>
            </Nav>
            
            <Nav className="ms-auto">
              {user?.jlpt_level && (
                <span className="jlpt-badge me-3 align-self-center">
                  JLPT {user.jlpt_level}
                </span>
              )}
              
              <Dropdown align="end">
                <Dropdown.Toggle variant="outline-primary" id="user-dropdown" className="border-0">
                  <i className="bi bi-person-circle me-2"></i>
                  {user?.full_name || user?.username}
                </Dropdown.Toggle>

                <Dropdown.Menu>
                  <Dropdown.ItemText>
                    <div className="d-flex align-items-center">
                      <i className="bi bi-person-circle fs-3 me-2 text-muted"></i>
                      <div>
                        <div className="fw-semibold">{user?.full_name}</div>
                        <small className="text-muted">{user?.email}</small>
                      </div>
                    </div>
                  </Dropdown.ItemText>
                  <Dropdown.Divider />
                  <Dropdown.Item href="/profile">
                    <i className="bi bi-gear me-2"></i>
                    Settings
                  </Dropdown.Item>
                  <Dropdown.Item href="/progress">
                    <i className="bi bi-graph-up me-2"></i>
                    Progress
                  </Dropdown.Item>
                  <Dropdown.Divider />
                  <Dropdown.Item onClick={logout} className="text-danger">
                    <i className="bi bi-box-arrow-right me-2"></i>
                    Sign Out
                  </Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
      
      <main className="flex-fill">
        {children}
      </main>
    </div>
  )
}

export default Layout
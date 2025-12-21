import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  Link,
} from "react-router-dom";
import "./App.css";
import { isAuthenticated, getUser, logout } from "./services/api";

// Import pages (will be created in components folder)
import AdminLogin from "./pages/AdminLogin";
import TenantLogin from "./pages/TenantLogin";
import UserLogin from "./pages/UserLogin";
import AdminDashboard from "./pages/AdminDashboard";
import TenantDashboard from "./pages/TenantDashboard";
import UserDashboard from "./pages/UserDashboard";
import TestTaking from "./pages/TestTaking";

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check if user is logged in
    if (isAuthenticated()) {
      const currentUser = getUser();
      setUser(currentUser);
    }
  }, []);

  const handleLogout = () => {
    logout();
    setUser(null);
  };

  return (
    <Router>
      <div className="App">
        {/* Navigation Bar */}
        <nav className="navbar">
          <div className="navbar-container">
            <Link to="/" className="navbar-logo">
              🏢 Multi-Tenant SaaS
            </Link>

            <div className="navbar-menu">
              {!user ? (
                <>
                  <Link to="/admin/login" className="navbar-item">
                    Admin Login
                  </Link>
                  <Link to="/tenant/login" className="navbar-item">
                    Tenant Login
                  </Link>
                  <Link to="/user/login" className="navbar-item">
                    User Login
                  </Link>
                </>
              ) : (
                <>
                  <span className="navbar-item">
                    Welcome, {user.name || user.email}
                  </span>
                  <button
                    onClick={handleLogout}
                    className="navbar-item logout-btn"
                  >
                    Logout
                  </button>
                </>
              )}
            </div>
          </div>
        </nav>

        {/* Routes */}
        <div className="content">
          <Routes>
            {/* Home Page */}
            <Route path="/" element={<HomePage />} />

            {/* Admin Routes */}
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route
              path="/admin/dashboard"
              element={
                <ProtectedRoute userType="admin">
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />

            {/* Tenant Routes */}
            <Route path="/tenant/login" element={<TenantLogin />} />
            <Route
              path="/tenant/dashboard"
              element={
                <ProtectedRoute userType="tenant">
                  <TenantDashboard />
                </ProtectedRoute>
              }
            />

            {/* User Routes */}
            <Route path="/user/login" element={<UserLogin />} />
            <Route path="/user/login/:slug" element={<UserLogin />} />
            <Route
              path="/user/dashboard"
              element={
                <ProtectedRoute userType="user">
                  <UserDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/test/:testId"
              element={
                <ProtectedRoute userType="user">
                  <TestTaking />
                </ProtectedRoute>
              }
            />

            {/* 404 Not Found */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>

        {/* Footer */}
        <footer className="footer">
          <p>&copy; 2025 Multi-Tenant SaaS Platform. All rights reserved.</p>
        </footer>
      </div>
    </Router>
  );
}

// Home Page Component
function HomePage() {
  return (
    <div className="home-page">
      <div className="hero-section">
        <h1>Welcome to Multi-Tenant SaaS Platform</h1>
        <p className="hero-subtitle">
          Scalable, Secure, and Modern B2B Platform
        </p>

        <div className="feature-grid">
          <div className="feature-card">
            <h3>🔐 Admin Portal</h3>
            <p>
              Manage tenants, monitor system activity, and control platform
              access
            </p>
            <Link to="/admin/login" className="btn btn-primary">
              Admin Login
            </Link>
          </div>

          <div className="feature-card">
            <h3>🏢 Tenant Portal</h3>
            <p>
              Manage your organization, employees, and customers efficiently
            </p>
            <Link to="/tenant/login" className="btn btn-primary">
              Tenant Login
            </Link>
          </div>

          <div className="feature-card">
            <h3>👥 User Portal</h3>
            <p>Access personalized services and manage your profile</p>
            <Link to="/user/login" className="btn btn-primary">
              User Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

// Protected Route Component
function ProtectedRoute({ children, userType }) {
  const authenticated = isAuthenticated();
  const user = getUser();

  if (!authenticated) {
    return <Navigate to={`/${userType}/login`} replace />;
  }

  if (user && user.user_type !== userType) {
    return <Navigate to="/" replace />;
  }

  return children;
}

// 404 Not Found Component
function NotFound() {
  return (
    <div className="not-found">
      <h1>404</h1>
      <p>Page not found</p>
      <Link to="/" className="btn btn-primary">
        Go Home
      </Link>
    </div>
  );
}

export default App;

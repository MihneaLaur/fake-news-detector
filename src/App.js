// src/App.js
import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./AuthContext";
import { NotificationProvider } from "./NotificationContext";
import NotificationContainer from "./components/NotificationContainer";
import QuickCheckModal from "./components/QuickCheckModal";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import History from "./pages/History";
import Settings from "./pages/Settings";
import AnalysisDetails from "./pages/AnalysisDetails";
import Admin from "./pages/Admin";
import "./App.css";

/**
 * Componenta principala a aplicatiei de detectie fake news.
 * Gestioneaza rutele, autentificarea si layout-ul general.
 */
function App() {
  const [isQuickCheckOpen, setIsQuickCheckOpen] = useState(false);

  /**
   * Handler global pentru Ctrl+K care deschide Quick Check modal.
   */
  useEffect(() => {
    const handleGlobalKeydown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setIsQuickCheckOpen(true);
      }
    };

    document.addEventListener('keydown', handleGlobalKeydown);
    return () => document.removeEventListener('keydown', handleGlobalKeydown);
  }, []);

  return (
    <NotificationProvider>
      <AuthProvider>
        <Router>
          <div className="app-bg">
            <Header onQuickCheckOpen={() => setIsQuickCheckOpen(true)} />
            <NavBar />
            <NotificationContainer />
            <QuickCheckModal 
              isOpen={isQuickCheckOpen} 
              onClose={() => setIsQuickCheckOpen(false)} 
            />
            <main className="main-content">
              <Routes>
                <Route path="/" element={<DefaultRoute />} />
                <Route path="/login" element={<RequireGuest><Login /></RequireGuest>} />
                <Route path="/register" element={<RequireGuest><Register /></RequireGuest>} />
                <Route path="/dashboard" element={
                  <RequireAuth><Dashboard /></RequireAuth>
                } />
                <Route path="/upload" element={
                  <RequireAuth><Upload /></RequireAuth>
                } />
                <Route path="/history" element={
                  <RequireAuth><History /></RequireAuth>
                } />
                <Route path="/settings" element={
                  <RequireAuth><Settings /></RequireAuth>
                } />
                <Route path="/analysis/:id" element={
                  <RequireAuth><AnalysisDetails /></RequireAuth>
                } />
                <Route path="/admin" element={
                  <RequireAdmin><Admin /></RequireAdmin>
                } />
              </Routes>
            </main>
          </div>
        </Router>
      </AuthProvider>
    </NotificationProvider>
  );
}

/**
 * Componenta header cu logo, titlu si sectiunea de profil.
 * @param {Function} onQuickCheckOpen - Functie pentru deschiderea Quick Check modal
 * @returns {JSX.Element} Header-ul aplicatiei
 */
function Header({ onQuickCheckOpen }) {
  const { user, logout } = useAuth(); 
  
  // Încarcă poza de profil din localStorage
  const profilePicture = user?.username ? localStorage.getItem(`profilePic_${user.username}`) : null;
  
  return (
    <header className="header">
      <span className="logo">📰</span>
      <h1 style={{ flex: 1 }}>Fake News Detector</h1>
      {user && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button 
            onClick={onQuickCheckOpen}
            style={{
              background: 'rgba(255, 255, 255, 0.2)',
              color: '#fff',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              borderRadius: '0.5rem',
              padding: '0.5rem 1rem',
              fontSize: '0.9rem',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
            onMouseEnter={(e) => {
              e.target.style.background = 'rgba(255, 255, 255, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.target.style.background = 'rgba(255, 255, 255, 0.2)';
            }}
          >
            🚀 Quick Check
            <span style={{ 
              fontSize: '0.7rem', 
              opacity: 0.8,
              background: 'rgba(255, 255, 255, 0.2)',
              padding: '0.1rem 0.3rem',
              borderRadius: '0.2rem'
            }}>
              Ctrl+K
            </span>
          </button>
          
          {/* 🆕 PROFILE SECTION */}
          <div style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            gap: '0.5rem' 
          }}>
            {/* Profile Picture */}
            <div style={{ position: 'relative' }}>
              {profilePicture ? (
                <img
                  src={profilePicture}
                  alt="Profile"
                  style={{
                    width: '45px',
                    height: '45px',
                    borderRadius: '50%',
                    objectFit: 'cover',
                    border: '2px solid rgba(255, 255, 255, 0.8)',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'scale(1.05)';
                    e.target.style.borderColor = 'rgba(255, 255, 255, 1)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'scale(1)';
                    e.target.style.borderColor = 'rgba(255, 255, 255, 0.8)';
                  }}
                  onClick={() => window.location.href = '/settings'}
                  title="Click pentru setări profil"
                />
              ) : (
                <div
                  style={{
                    width: '45px',
                    height: '45px',
                    borderRadius: '50%',
                    background: 'rgba(255, 255, 255, 0.2)',
                    border: '2px solid rgba(255, 255, 255, 0.8)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '1.2rem',
                    color: 'white',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'scale(1.05)';
                    e.target.style.background = 'rgba(255, 255, 255, 0.3)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'scale(1)';
                    e.target.style.background = 'rgba(255, 255, 255, 0.2)';
                  }}
                  onClick={() => window.location.href = '/settings'}
                  title="Click pentru setări profil"
                >
                  {user.username?.charAt(0).toUpperCase() || '👤'}
                </div>
              )}
              
              {/* Online indicator */}
              <div style={{
                position: 'absolute',
                bottom: '2px',
                right: '2px',
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                background: '#22c55e',
                border: '2px solid white',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.2)'
              }}></div>
            </div>
            
            {/* Username & Logout */}
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center',
              gap: '0.25rem'
            }}>
              <div style={{ 
                fontSize: '0.8rem', 
                color: 'rgba(255, 255, 255, 0.9)',
                fontWeight: '500',
                textAlign: 'center'
              }}>
                {user.username}
              </div>
              
              {/* 🆕 SETTINGS BUTTON */}
              <button 
                onClick={() => window.location.href = '/settings'}
                style={{
                  background: 'rgba(79, 70, 229, 0.8)',
                  color: 'white',
                  border: '1px solid rgba(79, 70, 229, 0.6)',
                  borderRadius: '0.3rem',
                  padding: '0.25rem 0.75rem',
                  fontSize: '0.7rem',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  marginBottom: '0.25rem'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = 'rgba(79, 70, 229, 1)';
                  e.target.style.transform = 'translateY(-1px)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = 'rgba(79, 70, 229, 0.8)';
                  e.target.style.transform = 'translateY(0)';
                }}
              >
                ⚙️ Setări
              </button>
              
              <button 
                onClick={logout}
                style={{
                  background: 'rgba(239, 68, 68, 0.8)',
                  color: 'white',
                  border: '1px solid rgba(239, 68, 68, 0.6)',
                  borderRadius: '0.3rem',
                  padding: '0.25rem 0.75rem',
                  fontSize: '0.7rem',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = 'rgba(239, 68, 68, 1)';
                  e.target.style.transform = 'translateY(-1px)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = 'rgba(239, 68, 68, 0.8)';
                  e.target.style.transform = 'translateY(0)';
                }}
              >
                Deconectare
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}

/**
 * Bara de navigatie cu linkuri specifice utilizatorului.
 * @returns {JSX.Element} Bara de navigatie cu optiuni contextuale
 */
function NavBar() {
  const { user } = useAuth();
  return (
    <nav className="navbar">
      {user && (
        <>
          <Link to="/dashboard" className="nav-btn">Dashboard</Link>
          <Link to="/upload" className="nav-btn">Încarcă</Link>
          <Link to="/history" className="nav-btn">Istoric</Link>
          {user.role === "admin" && <Link to="/admin" className="nav-btn">Admin</Link>}
        </>
      )}
      {!user && (
        <>
          <Link to="/login" className="nav-btn">Login</Link>
          <Link to="/register" className="nav-btn">Register</Link>
        </>
      )}
    </nav>
  );
}

/**
 * Componenta pentru ruta default care redirectioneaza utilizatorii.
 * @returns {JSX.Element} Navigate element cu redirectionare contextuala
 */
function DefaultRoute() {
  const { user } = useAuth();
  
  if (user) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return <Navigate to="/login" replace />;
}

/**
 * HOC pentru pagini accesibile doar utilizatorilor neautentificati.
 * @param {Object} props - Props cu children
 * @returns {JSX.Element} Children sau redirectionare la dashboard
 */
function RequireGuest({ children }) {
  const { user } = useAuth();
  return user ? <Navigate to="/dashboard" replace /> : children;
}

/**
 * HOC pentru pagini care necesita autentificare.
 * @param {Object} props - Props cu children
 * @returns {JSX.Element} Children sau redirectionare la login
 */
function RequireAuth({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" replace />;
}

/**
 * HOC pentru pagini care necesita privilegii de admin.
 * @param {Object} props - Props cu children
 * @returns {JSX.Element} Children sau redirectionare la login
 */
function RequireAdmin({ children }) {
  const { user } = useAuth();
  return user && user.role === "admin" ? children : <Navigate to="/login" replace />;
}

export default App;
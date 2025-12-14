import React from 'react'
import { Link } from 'react-router-dom'
import './Header.css'

const Header = () => {
  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <Link to="/" className="header-logo">
            <div className="logo-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                <path d="M9 12l2 2 4-4"/>
              </svg>
            </div>
            <span className="logo-title">Site Güvenlik Analizi</span>
          </Link>
          <nav className="header-nav">
            <Link to="/" className="nav-link">
              <span>Ana Sayfa</span>
            </Link>
            <Link to="/sites" className="nav-link">
              <span>Siteler</span>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  )
}

export default Header


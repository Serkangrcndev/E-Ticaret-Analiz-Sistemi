import React from 'react'
import { Link } from 'react-router-dom'
import RiskBadge from '../RiskBadge/RiskBadge'
import './SiteCard.css'

const SiteCard = ({ site, onClick }) => {
  const formatDate = (dateString) => {
    if (!dateString) return 'Henüz analiz edilmedi'
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('tr-TR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  }

  const handleClick = () => {
    if (onClick) {
      onClick(site.domain)
    }
  }

  return (
    <div className="site-card" onClick={handleClick}>
      <div className="site-card-header">
        <div className="site-card-info">
          <h3 className="site-card-title">{site.site_name || site.domain}</h3>
          <p className="site-card-domain">{site.domain}</p>
        </div>
        <RiskBadge score={site.risk_score || 0} />
      </div>
      <div className="site-card-footer">
        <div className="site-card-meta">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          <span>{formatDate(site.last_scanned_date)}</span>
        </div>
        <Link 
          to={`/site/${encodeURIComponent(site.domain)}`}
          className="site-card-link"
          onClick={(e) => e.stopPropagation()}
        >
          Detayları Gör
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="5" y1="12" x2="19" y2="12"/>
            <polyline points="12 5 19 12 12 19"/>
          </svg>
        </Link>
      </div>
    </div>
  )
}

export default SiteCard


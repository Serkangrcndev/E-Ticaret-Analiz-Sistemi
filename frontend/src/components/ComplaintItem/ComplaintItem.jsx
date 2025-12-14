import React from 'react'
import { SENTIMENT_COLORS, hexToRgba } from '../../utils/constants'
import './ComplaintItem.css'

const ComplaintItem = ({ complaint }) => {
  const formatDate = (dateString) => {
    if (!dateString) return 'Tarih bilgisi yok'
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('tr-TR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(date)
  }

  const getSourceName = (source) => {
    const sourceNames = {
      'sikayetvar': 'Şikayetvar',
      'trustpilot': 'Trustpilot',
      'google_reviews': 'Google Yorumlar'
    }
    return sourceNames[source] || source
  }

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 9V5a3 3 0 0 0-6 0v4"/>
            <rect x="2" y="9" width="20" height="12" rx="2" ry="2"/>
            <circle cx="12" cy="15" r="1"/>
          </svg>
        )
      case 'negative':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"/>
          </svg>
        )
      default:
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
        )
    }
  }

  const renderStars = (rating) => {
    if (!rating) return null
    return (
      <div className="complaint-rating">
        {[...Array(5)].map((_, i) => (
          <svg
            key={i}
            viewBox="0 0 24 24"
            fill={i < rating ? 'currentColor' : 'none'}
            stroke="currentColor"
            strokeWidth="2"
            className={i < rating ? 'star-filled' : 'star-empty'}
          >
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
        ))}
      </div>
    )
  }

  const sentiment = complaint.sentiment || 'neutral'
  const sentimentColor = SENTIMENT_COLORS[sentiment] || SENTIMENT_COLORS.neutral

  const isResolved = complaint.is_resolved || false

  return (
    <div className={`complaint-item ${isResolved ? 'complaint-resolved' : ''}`}>
      <div className="complaint-header">
        <div className="complaint-title-section">
          <div className="complaint-title-row">
            <h4 className="complaint-title">{complaint.title || 'Başlıksız Şikayet'}</h4>
            {isResolved && (
              <span className="complaint-resolved-badge">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                Çözüldü
              </span>
            )}
            {!isResolved && (
              <span className="complaint-unresolved-badge">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                Çözülmedi
              </span>
            )}
          </div>
          {complaint.source && (
            <span className={`complaint-source complaint-source-${complaint.source}`}>
              {getSourceName(complaint.source)}
            </span>
          )}
        </div>
        <div 
          className="complaint-sentiment"
          style={{ 
            '--sentiment-color': sentimentColor,
            '--sentiment-bg': hexToRgba(sentimentColor, 0.1)
          }}
        >
          {getSentimentIcon(sentiment)}
        </div>
      </div>
      
      {complaint.content && (
        <p className="complaint-content">{complaint.content}</p>
      )}

      <div className="complaint-footer">
        <div className="complaint-meta">
          {complaint.author && (
            <div className="complaint-author">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              <span>{complaint.author}</span>
            </div>
          )}
          {complaint.date && (
            <div className="complaint-date">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
              <span>{formatDate(complaint.date)}</span>
            </div>
          )}
        </div>
        {complaint.rating && renderStars(complaint.rating)}
      </div>

      {complaint.url && (
        <a
          href={complaint.url}
          target="_blank"
          rel="noopener noreferrer"
          className="complaint-link"
        >
          Orijinal Kaynağı Görüntüle
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
            <polyline points="15 3 21 3 21 9"/>
            <line x1="10" y1="14" x2="21" y2="3"/>
          </svg>
        </a>
      )}
    </div>
  )
}

export default ComplaintItem


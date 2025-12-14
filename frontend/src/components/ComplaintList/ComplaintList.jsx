import React, { useMemo, useState } from 'react'
import ComplaintItem from '../ComplaintItem/ComplaintItem'
import './ComplaintList.css'

const ComplaintList = ({ complaints, isLoading = false }) => {
  const [activeTab, setActiveTab] = useState(null)

  const getSourceName = (source) => {
    const sourceNames = {
      'sikayetvar': 'Şikayetvar',
      'trustpilot': 'Trustpilot',
      'google_reviews': 'Google Yorumlar'
    }
    return sourceNames[source] || source || 'Diğer'
  }

  const getSourceIcon = (source) => {
    switch (source) {
      case 'sikayetvar':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        )
      case 'trustpilot':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
        )
      case 'google_reviews':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
        )
      default:
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        )
    }
  }

  const getSourceColor = (source) => {
    switch (source) {
      case 'sikayetvar':
        return '#ef4444'
      case 'trustpilot':
        return '#6366f1'
      case 'google_reviews':
        return '#4285f4'
      default:
        return '#06b6d4'
    }
  }

  const categorizedComplaints = useMemo(() => {
    if (!complaints || complaints.length === 0) return {}
    
    const categorized = {}
    complaints.forEach(complaint => {
      const source = complaint.source || 'other'
      if (!categorized[source]) {
        categorized[source] = []
      }
      categorized[source].push(complaint)
    })
    
    return categorized
  }, [complaints])

  // İlk aktif tab'ı ayarla
  React.useEffect(() => {
    if (!activeTab && Object.keys(categorizedComplaints).length > 0) {
      const firstSource = Object.keys(categorizedComplaints)[0]
      setActiveTab(firstSource)
    }
  }, [categorizedComplaints, activeTab])

  if (isLoading) {
    return (
      <div className="complaint-list-loading">
        <div className="loading-skeleton">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="skeleton-item"></div>
          ))}
        </div>
      </div>
    )
  }

  if (!complaints || complaints.length === 0) {
    return (
      <div className="complaint-list-empty">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <h3>Henüz şikayet bulunamadı</h3>
        <p>Bu site için henüz kayıtlı şikayet bulunmuyor.</p>
      </div>
    )
  }

  const sourceOrder = ['sikayetvar', 'trustpilot', 'google_reviews', 'other']
  const availableSources = sourceOrder.filter(source => 
    categorizedComplaints[source] && categorizedComplaints[source].length > 0
  )

  return (
    <div className="complaint-list">
      <div className="complaint-list-header">
        <h2 className="complaint-list-title">
          Şikayetler ({complaints.length})
        </h2>
      </div>
      
      {/* Tab Navigation */}
      <div className="complaint-tabs">
        {availableSources.map(source => {
          const sourceName = getSourceName(source)
          const sourceColor = getSourceColor(source)
          const count = categorizedComplaints[source]?.length || 0
          
          return (
            <button
              key={source}
              className={`complaint-tab ${activeTab === source ? 'active' : ''}`}
              onClick={() => setActiveTab(source)}
              style={{ 
                '--source-color': sourceColor,
                borderBottomColor: activeTab === source ? sourceColor : 'transparent'
              }}
            >
              <div className="tab-icon">
                {getSourceIcon(source)}
              </div>
              <span className="tab-name">{sourceName}</span>
              <span className="tab-count">{count}</span>
            </button>
          )
        })}
      </div>

      {/* Tab Content */}
      <div className="complaint-tab-content">
        {activeTab && categorizedComplaints[activeTab] && (
          <div className="complaint-category-items">
            {categorizedComplaints[activeTab].map((complaint, index) => (
              <ComplaintItem key={index} complaint={complaint} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ComplaintList


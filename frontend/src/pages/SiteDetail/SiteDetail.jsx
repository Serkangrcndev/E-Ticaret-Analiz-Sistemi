import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import RiskBadge from '../../components/RiskBadge/RiskBadge'
import ComplaintList from '../../components/ComplaintList/ComplaintList'
import LoadingSpinner from '../../components/LoadingSpinner/LoadingSpinner'
import { apiService } from '../../services/api'
import { getRiskLevel, SENTIMENT_COLORS, hexToRgba } from '../../utils/constants'
import './SiteDetail.css'

const SiteDetail = () => {
  const { domain } = useParams()
  const navigate = useNavigate()
  const [siteInfo, setSiteInfo] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  useEffect(() => {
    loadSiteInfo()
  }, [domain])

  const loadSiteInfo = async () => {
    try {
      setIsLoading(true)
      setError('')
      const decodedDomain = decodeURIComponent(domain)
      const info = await apiService.getSiteInfo(decodedDomain)
      setSiteInfo(info)
    } catch (err) {
      setError(err.message || 'Site bilgileri yüklenirken bir hata oluştu')
      console.error('Site bilgisi yükleme hatası:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleReanalyze = async () => {
    if (!siteInfo) return

    setIsAnalyzing(true)
    setError('')

    try {
      const url = `https://${siteInfo.domain}`
      const result = await apiService.analyzeSite(url)
      
      if (result.error) {
        setError(result.error)
        setIsAnalyzing(false)
        return
      }

      // Yeniden analiz başarılı, sayfayı yenile
      await loadSiteInfo()
      setIsAnalyzing(false)
    } catch (err) {
      setError(err.message || 'Analiz sırasında bir hata oluştu')
      setIsAnalyzing(false)
    }
  }

  if (isLoading) {
    return (
      <div className="site-detail">
        <div className="container">
          <div className="site-detail-loading">
            <LoadingSpinner size="large" text="Site bilgileri yükleniyor..." />
          </div>
        </div>
      </div>
    )
  }

  if (error && !siteInfo) {
    return (
      <div className="site-detail">
        <div className="container">
          <div className="site-detail-error">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <h2>Hata</h2>
            <p>{error}</p>
            <div className="error-actions">
              <Link to="/" className="button-primary">
                Ana Sayfaya Dön
              </Link>
              <button onClick={loadSiteInfo} className="button-secondary">
                Tekrar Dene
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!siteInfo) {
    return null
  }

  const riskLevel = getRiskLevel(siteInfo.risk_score || 0)
  const statistics = siteInfo.statistics || {
    total: 0,
    negative: 0,
    positive: 0,
    neutral: 0,
    resolved: 0,
    unresolved: 0
  }

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

  return (
    <div className="site-detail">
      <div className="container">
        <Link to="/" className="back-button">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          <span>Ana Sayfaya Dön</span>
        </Link>

        {/* Site Header */}
        <div className="site-header">
          <div className="site-header-content">
            <div className="site-header-info">
              <h1 className="site-name">{siteInfo.site_name || siteInfo.domain}</h1>
              <p className="site-domain">{siteInfo.domain}</p>
            </div>
            <div className="site-header-actions">
              <RiskBadge score={siteInfo.risk_score || 0} />
              <button
                onClick={handleReanalyze}
                disabled={isAnalyzing}
                className="reanalyze-button"
              >
                {isAnalyzing ? (
                  <>
                    <span className="button-spinner"></span>
                    <span>Analiz Ediliyor...</span>
                  </>
                ) : (
                  <>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="23 4 23 10 17 10"/>
                      <polyline points="1 20 1 14 7 14"/>
                      <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
                    </svg>
                    <span>Yeniden Analiz Et</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className="error-message fade-in">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Statistics */}
        <div className="statistics-section">
          <div className="statistics-grid">
            <div className="stat-card">
              <div 
                className="stat-icon" 
                style={{ 
                  '--stat-color': '#6366f1',
                  '--stat-bg': hexToRgba('#6366f1', 0.1)
                }}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
              </div>
              <div className="stat-content">
                <div className="stat-value">{statistics.total}</div>
                <div className="stat-label">Toplam Şikayet</div>
              </div>
            </div>

            <div className="stat-card">
              <div 
                className="stat-icon" 
                style={{ 
                  '--stat-color': SENTIMENT_COLORS.negative,
                  '--stat-bg': hexToRgba(SENTIMENT_COLORS.negative, 0.1)
                }}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"/>
                </svg>
              </div>
              <div className="stat-content">
                <div className="stat-value">{statistics.negative}</div>
                <div className="stat-label">Negatif</div>
              </div>
            </div>

            <div className="stat-card">
              <div 
                className="stat-icon" 
                style={{ 
                  '--stat-color': SENTIMENT_COLORS.positive,
                  '--stat-bg': hexToRgba(SENTIMENT_COLORS.positive, 0.1)
                }}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 9V5a3 3 0 0 0-6 0v4"/>
                  <rect x="2" y="9" width="20" height="12" rx="2" ry="2"/>
                  <circle cx="12" cy="15" r="1"/>
                </svg>
              </div>
              <div className="stat-content">
                <div className="stat-value">{statistics.positive}</div>
                <div className="stat-label">Pozitif</div>
              </div>
            </div>

            <div className="stat-card">
              <div 
                className="stat-icon" 
                style={{ 
                  '--stat-color': SENTIMENT_COLORS.neutral,
                  '--stat-bg': hexToRgba(SENTIMENT_COLORS.neutral, 0.1)
                }}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
              </div>
              <div className="stat-content">
                <div className="stat-value">{statistics.neutral}</div>
                <div className="stat-label">Nötr</div>
              </div>
            </div>

            <div className="stat-card">
              <div 
                className="stat-icon" 
                style={{ 
                  '--stat-color': '#10b981',
                  '--stat-bg': hexToRgba('#10b981', 0.1)
                }}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
              </div>
              <div className="stat-content">
                <div className="stat-value">{statistics.resolved || 0}</div>
                <div className="stat-label">Çözüldü</div>
              </div>
            </div>

            <div className="stat-card">
              <div 
                className="stat-icon" 
                style={{ 
                  '--stat-color': '#ef4444',
                  '--stat-bg': hexToRgba('#ef4444', 0.1)
                }}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
              </div>
              <div className="stat-content">
                <div className="stat-value">{statistics.unresolved || 0}</div>
                <div className="stat-label">Çözülmedi</div>
              </div>
            </div>
          </div>
        </div>

        {/* Meta Information */}
        <div className="meta-section">
          <div className="meta-item">
            <span className="meta-label">Son Analiz:</span>
            <span className="meta-value">{formatDate(siteInfo.last_scanned_date)}</span>
          </div>
          {siteInfo.created_date && (
            <div className="meta-item">
              <span className="meta-label">İlk Analiz:</span>
              <span className="meta-value">{formatDate(siteInfo.created_date)}</span>
            </div>
          )}
        </div>

        {/* Complaints */}
        <div className="complaints-section">
          <ComplaintList 
            complaints={siteInfo.complaints || []} 
            isLoading={isAnalyzing}
          />
        </div>
      </div>
    </div>
  )
}

export default SiteDetail


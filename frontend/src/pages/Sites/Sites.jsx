import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import SiteCard from '../../components/SiteCard/SiteCard'
import LoadingSpinner from '../../components/LoadingSpinner/LoadingSpinner'
import { apiService } from '../../services/api'
import './Sites.css'

const Sites = () => {
  const [sites, setSites] = useState([])
  const [isLoadingSites, setIsLoadingSites] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    loadSites()
  }, [])

  const loadSites = async () => {
    try {
      setIsLoadingSites(true)
      setError('')
      const response = await apiService.getAllSites()
      setSites(response.sites || [])
    } catch (err) {
      setError(err.message)
      console.error('Siteler yüklenirken hata:', err)
    } finally {
      setIsLoadingSites(false)
    }
  }

  const handleSiteClick = (domain) => {
    navigate(`/site/${encodeURIComponent(domain)}`)
  }

  return (
    <div className="sites-page">
      <div className="container">
        <div className="sites-page-header">
          <div className="sites-header-content">
            <h1 className="sites-page-title">
              Analiz Edilmiş <span className="gradient-text">Siteler</span>
            </h1>
            <p className="sites-page-description">
              Güvenlik analizi yapılmış tüm siteleri burada görüntüleyebilirsiniz.
            </p>
          </div>
          <button 
            onClick={loadSites}
            className="refresh-button"
            disabled={isLoadingSites}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="23 4 23 10 17 10"/>
              <polyline points="1 20 1 14 7 14"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
            <span>Yenile</span>
          </button>
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

        {isLoadingSites ? (
          <div className="sites-loading">
            <LoadingSpinner size="large" text="Siteler yükleniyor..." />
          </div>
        ) : sites.length === 0 ? (
          <div className="sites-empty">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
              <line x1="12" y1="22.08" x2="12" y2="12"/>
            </svg>
            <h3>Henüz analiz edilmiş site yok</h3>
            <p>Ana sayfadaki arama kutusunu kullanarak bir site analizi başlatın.</p>
            <button 
              onClick={() => navigate('/')}
              className="button-primary"
            >
              Ana Sayfaya Dön
            </button>
          </div>
        ) : (
          <div className="sites-grid">
            {sites.map((site, index) => (
              <SiteCard
                key={index}
                site={site}
                onClick={handleSiteClick}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Sites


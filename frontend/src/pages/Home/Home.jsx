import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import SearchBar from '../../components/SearchBar/SearchBar'
import { apiService } from '../../services/api'
import './Home.css'

const Home = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState('')
  const [dbStatus, setDbStatus] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    checkDbStatus()
  }, [])

  const checkDbStatus = async () => {
    try {
      const status = await apiService.checkDbStatus()
      setDbStatus(status)
    } catch (err) {
      setDbStatus({ connected: false, message: err.message })
    }
  }

  const handleSearch = async (url) => {
    setIsAnalyzing(true)
    setError('')

    try {
      const result = await apiService.analyzeSite(url)
      
      if (result.error) {
        setError(result.error)
        setIsAnalyzing(false)
        return
      }

      const domain = result.domain || url.replace(/^https?:\/\//, '').replace(/^www\./, '').split('/')[0]
      navigate(`/site/${encodeURIComponent(domain)}`)
    } catch (err) {
      setError(err.message || 'Analiz sırasında bir hata oluştu')
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="home-new">
      {/* Animated Background Elements */}
      <div className="bg-animation">
        <div className="bg-circle bg-circle-1"></div>
        <div className="bg-circle bg-circle-2"></div>
        <div className="bg-circle bg-circle-3"></div>
        <div className="bg-circle bg-circle-4"></div>
      </div>

      <div className="container">
        {/* Hero Section - Completely Redesigned */}
        <section className="hero-new">
          <div className="hero-badge">
            <span className="badge-dot"></span>
            <span>Güvenli Alışveriş İçin Akıllı Çözüm</span>
          </div>
          
          <h1 className="hero-title-new">
            Online Alışverişte
            <br />
            <span className="title-highlight">Güvenli</span> Kararlar Verin
          </h1>
          
          <p className="hero-subtitle">
            Site güvenlik analizi ile alışveriş yapmadan önce sitenin güvenilirliğini öğrenin. 
            <br />
            Şikayet analizi ve risk skorları ile bilinçli kararlar verin.
          </p>

          <div className="search-wrapper-new">
            <SearchBar onSearch={handleSearch} isLoading={isAnalyzing} />
            {error && (
              <div className="error-message-new fade-in">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <span>{error}</span>
              </div>
            )}
          </div>

          {/* Stats Preview */}
          <div className="hero-stats">
            <div className="stat-preview">
              <div className="stat-preview-icon">🔍</div>
              <div className="stat-preview-content">
                <div className="stat-preview-value">Anında</div>
                <div className="stat-preview-label">Analiz</div>
              </div>
            </div>
            <div className="stat-preview">
              <div className="stat-preview-icon">📊</div>
              <div className="stat-preview-content">
                <div className="stat-preview-value">Detaylı</div>
                <div className="stat-preview-label">Raporlar</div>
              </div>
            </div>
            <div className="stat-preview">
              <div className="stat-preview-icon">🛡️</div>
              <div className="stat-preview-content">
                <div className="stat-preview-value">Güvenli</div>
                <div className="stat-preview-label">Alışveriş</div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section - New Design */}
        <section className="features-new">
          <div className="section-intro">
            <h2 className="section-title-new">Neden Bizi Seçmelisiniz?</h2>
            <p className="section-subtitle">Güvenli alışveriş için ihtiyacınız olan her şey</p>
          </div>

          <div className="features-grid-new">
            <div className="feature-box">
              <div className="feature-box-header">
                <div className="feature-icon-box">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    <path d="M9 12l2 2 4-4"/>
                  </svg>
                </div>
                <h3>Güvenilir Kaynaklar</h3>
              </div>
              <p>Şikayetvar gibi güvenilir platformlardan toplanan gerçek kullanıcı şikayetleri</p>
            </div>

            <div className="feature-box">
              <div className="feature-box-header">
                <div className="feature-icon-box">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                  </svg>
                </div>
                <h3>Hızlı Sonuçlar</h3>
              </div>
              <p>Birkaç dakika içinde kapsamlı güvenlik analizi ve risk skoru</p>
            </div>

            <div className="feature-box">
              <div className="feature-box-header">
                <div className="feature-icon-box">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                    <path d="M2 17l10 5 10-5"/>
                    <path d="M2 12l10 5 10-5"/>
                  </svg>
                </div>
                <h3>Kapsamlı Analiz</h3>
              </div>
              <p>Risk skorları, sentiment analizi ve çözülmüş şikayet takibi</p>
            </div>

            <div className="feature-box">
              <div className="feature-box-header">
                <div className="feature-icon-box">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                  </svg>
                </div>
                <h3>Güvenli Alışveriş</h3>
              </div>
              <p>Alışveriş yapmadan önce sitenin güvenilirliğini kontrol edin</p>
            </div>
          </div>
        </section>

        {/* How It Works - New Design */}
        <section className="how-it-works-new">
          <div className="section-intro">
            <h2 className="section-title-new">Nasıl Çalışır?</h2>
            <p className="section-subtitle">4 basit adımda güvenli alışveriş</p>
          </div>

          <div className="steps-container">
            <div className="step-item">
              <div className="step-icon-circle">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 21l-6-6m2-5a7 7 0 1 1-14 0 7 7 0 0 1 14 0z"/>
                </svg>
                <div className="step-pulse"></div>
              </div>
              <div className="step-number">01</div>
              <div className="step-content">
                <h3>URL Girin</h3>
                <p>Analiz etmek istediğiniz sitenin URL'sini girin</p>
              </div>
              <div className="step-arrow-right">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
              </div>
            </div>

            <div className="step-item">
              <div className="step-icon-circle">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                </svg>
                <div className="step-pulse"></div>
              </div>
              <div className="step-number">02</div>
              <div className="step-content">
                <h3>Otomatik Tarama</h3>
                <p>Sistemimiz şikayet kaynaklarını otomatik olarak tarar</p>
              </div>
              <div className="step-arrow-right">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
              </div>
            </div>

            <div className="step-item">
              <div className="step-icon-circle">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                  <path d="M2 17l10 5 10-5"/>
                  <path d="M2 12l10 5 10-5"/>
                </svg>
                <div className="step-pulse"></div>
              </div>
              <div className="step-number">03</div>
              <div className="step-content">
                <h3>Analiz & Skorlama</h3>
                <p>Toplanan veriler analiz edilir ve risk skoru hesaplanır</p>
              </div>
              <div className="step-arrow-right">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
              </div>
            </div>

            <div className="step-item">
              <div className="step-icon-circle">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                </svg>
                <div className="step-pulse"></div>
              </div>
              <div className="step-number">04</div>
              <div className="step-content">
                <h3>Detaylı Rapor</h3>
                <p>Kapsamlı güvenlik raporu ve önerileri görüntüleyin</p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section - Redesigned */}
        <section className="cta-section">
          <div className="cta-container">
            <div className="cta-text">
              <h2>Güvenli Alışverişe Başlayın</h2>
              <p>Site güvenilirliğini kontrol edin ve bilinçli kararlar verin</p>
            </div>
            <div className="cta-buttons">
              <Link to="/sites" className="cta-button-primary">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 21l-6-6m2-5a7 7 0 1 1-14 0 7 7 0 0 1 14 0z"/>
                </svg>
                <span>Analiz Edilmiş Siteler</span>
              </Link>
            </div>
          </div>
        </section>

        {/* DB Warning */}
        {dbStatus && !dbStatus.connected && (
          <div className="db-warning-new fade-in">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <div>
              <strong>Veritabanı Bağlantı Uyarısı</strong>
              <p>{dbStatus.message}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Home

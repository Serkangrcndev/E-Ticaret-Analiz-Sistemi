import React from 'react'
import { Link } from 'react-router-dom'
import './Footer.css'

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-section">
            <h3>Site Güvenlik Analizi</h3>
            <p>Güvenli alışveriş için site güvenilirliğini kontrol edin</p>
          </div>
          
          <div className="footer-section">
            <h4>Hızlı Linkler</h4>
            <ul>
              <li><Link to="/">Ana Sayfa</Link></li>
              <li><Link to="/sites">Analiz Edilmiş Siteler</Link></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Kaynaklar</h4>
            <ul>
              <li><a href="https://www.sikayetvar.com" target="_blank" rel="noopener noreferrer">Şikayetvar</a></li>
              <li><a href="https://www.trustpilot.com" target="_blank" rel="noopener noreferrer">Trustpilot</a></li>
            </ul>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; {new Date().getFullYear()} Site Güvenlik Analizi. Tüm hakları saklıdır.</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer


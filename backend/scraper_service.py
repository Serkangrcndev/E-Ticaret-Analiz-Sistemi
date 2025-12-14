from scrapers.sikayetvar_scraper import SikayetvarScraper
from scrapers.trustpilot_scraper import TrustpilotScraper
from scrapers.google_reviews_scraper import GoogleReviewsScraper
from database import Database
import logging
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ScraperService:
    def __init__(self):
        self.db = Database()
        self.scrapers = {
            'sikayetvar': SikayetvarScraper(),
            'trustpilot': TrustpilotScraper(),
            'google_reviews': GoogleReviewsScraper()
        }
    
    def extract_domain(self, url):
        """URL'den domain çıkar"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            # www. ve protokolü temizle
            domain = domain.replace('www.', '').replace('https://', '').replace('http://', '')
            return domain
        except:
            return url
    
    def extract_site_name(self, domain):
        """Domain'den site adını çıkar"""
        # Domain'den .com, .net gibi uzantıları kaldır
        site_name = domain.split('.')[0]
        return site_name.capitalize()
    
    def calculate_risk_score(self, complaints):
        """Şikayetlere göre risk skoru hesapla"""
        if not complaints:
            return 0
        
        total = len(complaints)
        negative_count = sum(1 for c in complaints if c.get('sentiment') == 'negative')
        positive_count = sum(1 for c in complaints if c.get('sentiment') == 'positive')
        
        # Risk skoru: 0-100 arası
        # Negatif yorumlar riski artırır, pozitif yorumlar azaltır
        negative_ratio = negative_count / total if total > 0 else 0
        positive_ratio = positive_count / total if total > 0 else 0
        
        risk_score = int((negative_ratio * 80) - (positive_ratio * 20) + 20)
        risk_score = max(0, min(100, risk_score))  # 0-100 arası sınırla
        
        return risk_score
    
    def determine_risk_level(self, risk_score):
        """Risk skoruna göre risk seviyesi belirle"""
        if risk_score >= 75:
            return 'Critical'
        elif risk_score >= 50:
            return 'High'
        elif risk_score >= 25:
            return 'Medium'
        else:
            return 'Low'
    
    def scrape_all_sources(self, domain, site_name):
        """Tüm kaynaklardan veri topla"""
        all_complaints = []
        
        for source_name, scraper in self.scrapers.items():
            try:
                logger.info(f"→ {source_name} scraping başlatılıyor...")
                complaints = scraper.scrape(domain, site_name)
                # Her complaint'e source ekle
                for complaint in complaints:
                    complaint['source'] = source_name
                all_complaints.extend(complaints)
                logger.info(f"✓ {source_name}'dan {len(complaints)} kayıt bulundu")
            except Exception as e:
                logger.error(f"✗ {source_name} scraping hatası: {str(e)}")
        
        return all_complaints
    
    def process_site(self, url):
        """Site için tüm işlemleri gerçekleştir"""
        import time
        start_time = time.time()
        
        try:
            # Domain ve site adını çıkar
            domain = self.extract_domain(url)
            site_name = self.extract_site_name(domain)
            
            logger.info(f"→ Site işleniyor: {domain} ({site_name})")
            
            # Veritabanına bağlan (scraping için pool kullan)
            if not self.db.connect():
                return {'error': 'Veritabanı bağlantı hatası'}
            
            # Site'yi getir veya oluştur
            site_id = self.db.get_or_create_site(domain)
            
            # Tüm kaynaklardan veri topla
            all_complaints = self.scrape_all_sources(domain, site_name)
            
            # Verileri veritabanına kaydet (cache'den gelenleri hariç tut)
            saved_count = 0
            for complaint in all_complaints:
                # Cache'den gelen veriler DB'ye kaydedilmez
                if complaint.get('cached'):
                    logger.debug(f"⚡ Cache'den gelen veri DB'ye kaydedilmedi: {complaint.get('title')}")
                    continue
                
                if self.db.save_complaint(
                    site_id=site_id,
                    source=complaint.get('source', 'unknown'),
                    title=complaint.get('title', ''),
                    content=complaint.get('content', ''),
                    author=complaint.get('author', ''),
                    date=complaint.get('date'),
                    rating=complaint.get('rating'),
                    sentiment=complaint.get('sentiment', 'neutral'),
                    url=complaint.get('url', ''),
                    is_resolved=complaint.get('is_resolved', False)
                ):
                    saved_count += 1
            
            # Risk skorunu hesapla ve güncelle
            risk_score = self.calculate_risk_score(all_complaints)
            risk_level = self.determine_risk_level(risk_score)
            self.db.update_site_risk_score(site_id, risk_score)
            
            # Scraping geçmişini kaydet (her kaynak için ayrı süre hesapla)
            scraping_start = time.time()
            for source_name in self.scrapers.keys():
                source_start = time.time()
                source_complaints = [c for c in all_complaints if c.get('source') == source_name]
                source_duration = int(time.time() - source_start)
                
                self.db.save_scraping_history(
                    site_id=site_id,
                    source=source_name,
                    status='Success' if source_complaints else 'Failed',
                    records_found=len(source_complaints),
                    duration=source_duration
                )
            
            total_duration = int(time.time() - start_time)
            
            self.db.close(force=False)  # Pool'da tut, scraping sık yapılabilir
            
            return {
                'success': True,
                'site_id': site_id,
                'domain': domain,
                'site_name': site_name,
                'total_complaints': len(all_complaints),
                'saved_count': saved_count,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'duration': total_duration
            }
            
        except Exception as e:
            logger.error(f"✗ Site işleme hatası: {str(e)}")
            if self.db.conn:
                self.db.close()
            return {'error': str(e)}


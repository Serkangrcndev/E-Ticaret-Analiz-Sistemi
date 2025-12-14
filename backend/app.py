from flask import Flask, request, jsonify
from flask_cors import CORS
from scraper_service import ScraperService
from database import Database
import logging
from config import API_HOST, API_PORT, DEBUG
import signal
import sys

# Logging format with Serkan Gurcan branding
logging.basicConfig(
    level=logging.INFO,
    format='[AKTIF] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Frontend'den erişim için

# Timeout ayarları (scraping uzun sürebilir)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['PERMANENT_SESSION_LIFETIME'] = 600  # 10 dakika

scraper_service = ScraperService()

# Graceful shutdown
def signal_handler(sig, frame):
    logger.info('Shutting down gracefully...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

@app.route('/', methods=['GET'])
def root():
    """Ana sayfa - API bilgisi"""
    return jsonify({
        'message': 'Site Güvenlik Analizi API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'db-status': '/api/db-status',
            'analyze': '/api/analyze (POST)',
            'site': '/api/site/<domain>',
            'sites': '/api/sites',
            'init-db': '/api/init-db (POST)',
            'migrate-isresolved': '/api/migrate-isresolved (POST)'
        }
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """API sağlık kontrolü"""
    return jsonify({'status': 'ok', 'message': 'API çalışıyor'})

@app.route('/api/db-status', methods=['GET'])
def db_status():
    """Veritabanı bağlantı durumunu kontrol et (pool kullanır)"""
    try:
        db = Database(use_pool=True)  # Pool kullan
        is_connected = db.test_connection()
        if is_connected:
            db.close(force=False)  # Pool'da tut, kapatma
            return jsonify({
                'status': 'connected',
                'message': 'Veritabanı bağlantısı başarılı',
                'connected': True
            }), 200
        else:
            error_msg = "Veritabanı bağlantısı başarısız. SQL Server çalışıyor mu?"
            return jsonify({
                'status': 'disconnected',
                'message': error_msg,
                'connected': False,
                'help': 'test_db_connection.py scriptini çalıştırarak bağlantıyı test edin'
            }), 200  # 200 döndür ki frontend hata mesajını gösterebilsin
    except Exception as e:
        logger.error(f"DB status kontrolü hatası: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'connected': False,
            'help': 'SQL Server çalışıyor mu? test_db_connection.py scriptini çalıştırın'
        }), 200  # 200 döndür ki frontend hata mesajını gösterebilsin

@app.route('/api/analyze', methods=['POST'])
def analyze_site():
    """Site analizi başlat (async benzeri - uzun sürebilir)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Geçersiz istek'}), 400
            
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL gerekli'}), 400
        
        logger.info(f"Site analizi başlatılıyor: {url}")
        
        # Site analizini başlat (bu işlem uzun sürebilir - 5-10 dakika)
        # Not: Production'da background task kullanılmalı
        try:
            result = scraper_service.process_site(url)
            
            if 'error' in result:
                logger.error(f"Analiz hatası: {result.get('error')}")
                return jsonify(result), 500
            
            logger.info(f"Analiz tamamlandı: {result.get('total_complaints', 0)} kayıt bulundu")
            return jsonify(result), 200
            
        except KeyboardInterrupt:
            logger.warning("Analiz kullanıcı tarafından iptal edildi")
            return jsonify({'error': 'Analiz iptal edildi'}), 500
        except Exception as e:
            logger.error(f"Analiz sırasında hata: {str(e)}", exc_info=True)
            return jsonify({'error': f'Analiz hatası: {str(e)}'}), 500
        
    except Exception as e:
        logger.error(f"Analiz endpoint hatası: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/site/<domain>', methods=['GET'])
def get_site_info(domain):
    """Site bilgilerini getir"""
    db = None
    try:
        db = Database(use_pool=True)
        if not db.connect():
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
        
        # Site bilgileri için ayrı cursor - fetchall kullan ve hemen kapat
        site_row = None
        try:
            cursor1 = db.conn.cursor()
            cursor1.execute("""
                SELECT SiteID, Domain, SiteName, RiskScore, LastScannedDate, CreatedDate
                FROM Sites WHERE Domain = ?
            """, (domain,))
            rows = cursor1.fetchall()
            cursor1.close()  # Cursor'ı hemen kapat
            
            if not rows or len(rows) == 0:
                db.close(force=False)
                return jsonify({'error': 'Site bulunamadı'}), 404
            
            site_row = rows[0]
        except Exception as e:
            logger.error(f"Site bilgisi çekme hatası: {str(e)}")
            db.close(force=True)
            return jsonify({'error': f'Site bilgisi çekilemedi: {str(e)}'}), 500
        
        site_info = {
            'site_id': site_row[0],
            'domain': site_row[1],
            'site_name': site_row[2],
            'risk_score': site_row[3],
            'last_scanned_date': site_row[4].isoformat() if site_row[4] else None,
            'created_date': site_row[5].isoformat() if site_row[5] else None
        }
        
        # Şikayetler için ayrı cursor - fetchall kullan ve hemen kapat
        complaints = []
        resolved_count = 0
        unresolved_count = 0
        try:
            cursor2 = db.conn.cursor()
            cursor2.execute("""
                SELECT Source, Title, Content, Author, Date, Rating, Sentiment, URL, IsResolved
                FROM Complaints WHERE SiteID = ? ORDER BY Date DESC
            """, (site_row[0],))
            
            rows = cursor2.fetchall()  # Tüm sonuçları al
            cursor2.close()  # Cursor'ı hemen kapat
            
            # Sonuçları işle
            for row in rows:
                is_resolved = bool(row[8]) if row[8] is not None else False
                if is_resolved:
                    resolved_count += 1
                else:
                    unresolved_count += 1
                    
                complaints.append({
                    'source': row[0],
                    'title': row[1],
                    'content': row[2],
                    'author': row[3],
                    'date': row[4].isoformat() if row[4] else None,
                    'rating': row[5],
                    'sentiment': row[6],
                    'url': row[7],
                    'is_resolved': is_resolved
                })
        except Exception as e:
            logger.error(f"Şikayetler çekme hatası: {str(e)}")
            # Hata olsa bile devam et, boş liste döndür
        
        site_info['complaints'] = complaints
        site_info['total_complaints'] = len(complaints)
        
        # Risk analizi
        negative_count = sum(1 for c in complaints if c['sentiment'] == 'negative')
        positive_count = sum(1 for c in complaints if c['sentiment'] == 'positive')
        
        site_info['statistics'] = {
            'total': len(complaints),
            'negative': negative_count,
            'positive': positive_count,
            'neutral': len(complaints) - negative_count - positive_count,
            'resolved': resolved_count,
            'unresolved': unresolved_count
        }
        
        db.close(force=False)  # Pool'da tut
        return jsonify(site_info), 200
        
    except Exception as e:
        logger.error(f"Site bilgisi getirme hatası: {str(e)}")
        # Hata durumunda bağlantıyı kapat
        if db:
            try:
                db.close(force=True)
            except:
                pass
        return jsonify({'error': str(e)}), 500

@app.route('/api/sites', methods=['GET'])
def get_all_sites():
    """Tüm siteleri listele"""
    db = None
    try:
        db = Database(use_pool=True)
        if not db.connect():
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
        
        sites = []
        try:
            cursor = db.conn.cursor()
            cursor.execute("""
                SELECT Domain, SiteName, RiskScore, LastScannedDate
                FROM Sites ORDER BY LastScannedDate DESC
            """)
            
            rows = cursor.fetchall()  # Tüm sonuçları al
            cursor.close()  # Cursor'ı hemen kapat
            
            # Sonuçları işle
            for row in rows:
                sites.append({
                    'domain': row[0],
                    'site_name': row[1],
                    'risk_score': row[2],
                    'last_scanned_date': row[3].isoformat() if row[3] else None
                })
        except Exception as e:
            logger.error(f"Siteler çekme hatası: {str(e)}")
            # Hata olsa bile devam et, boş liste döndür
        
        db.close(force=False)  # Pool'da tut
        return jsonify({'sites': sites}), 200
        
    except Exception as e:
        logger.error(f"Siteleri listeleme hatası: {str(e)}")
        # Hata durumunda bağlantıyı kapat
        if db:
            try:
                db.close(force=True)
            except:
                pass
        return jsonify({'error': str(e)}), 500

@app.route('/api/init-db', methods=['POST'])
def init_database():
    """Veritabanı tablolarını oluştur"""
    try:
        db = Database(use_pool=False)  # Tablo oluşturma için pool kullanma
        if not db.connect():
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
        
        if db.create_tables():
            # Migration: IsResolved sütununu ekle (eğer yoksa)
            db.migrate_add_isresolved_column()
            db.close(force=True)  # Tablo oluşturma sonrası kapat
            return jsonify({'message': 'Veritabanı tabloları başarıyla oluşturuldu'}), 200
        else:
            db.close(force=True)
            return jsonify({'error': 'Tablo oluşturma hatası'}), 500
            
    except Exception as e:
        logger.error(f"Veritabanı başlatma hatası: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/migrate-isresolved', methods=['POST'])
def migrate_isresolved():
    """Complaints tablosuna IsResolved sütunu ekle (migration)"""
    try:
        db = Database(use_pool=False)
        if not db.connect():
            return jsonify({'error': 'Veritabanı bağlantı hatası'}), 500
        
        if db.migrate_add_isresolved_column():
            db.close(force=True)
            return jsonify({'message': 'IsResolved sütunu başarıyla eklendi'}), 200
        else:
            db.close(force=True)
            return jsonify({'error': 'IsResolved sütunu eklenirken hata oluştu'}), 500
            
    except Exception as e:
        logger.error(f"Migration hatası: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Erişim URL'lerini belirle
    if API_HOST == '0.0.0.0':
        access_urls = [
            f"http://localhost:{API_PORT}",
            f"http://127.0.0.1:{API_PORT}",
            f"http://0.0.0.0:{API_PORT} (tüm interface'ler)"
        ]
    else:
        access_urls = [f"http://{API_HOST}:{API_PORT}"]
    
    if DEBUG:
        logger.info("=" * 60)
        logger.info("🚀 Development Server Başlatılıyor")
        logger.info("=" * 60)
        logger.info("Erişim URL'leri:")
        for url in access_urls:
            logger.info(f"  → {url}")
        logger.info("=" * 60)
        logger.warning("⚠️  Bu bir development server'dır. Production için WSGI server kullanın!")
        logger.info("=" * 60)
        app.run(host=API_HOST, port=API_PORT, debug=DEBUG, threaded=True)
    else:
        # Production modunda Waitress kullan
        try:
            from waitress import serve
            logger.info("=" * 60)
            logger.info("🚀 Scraper Servisi Başlatılıyor")
            logger.info("=" * 60)
            logger.info("Erişim URL'leri:")
            for url in access_urls:
                logger.info(f"  → {url}")
            logger.info("=" * 60)
            serve(app, host=API_HOST, port=API_PORT, threads=4, channel_timeout=600)
        except ImportError:
            logger.warning("Waitress yüklü değil, development server kullanılıyor")
            logger.warning("Production için: pip install waitress")
            logger.info("=" * 60)
            logger.info("🚀 Server Başlatılıyor")
            logger.info("=" * 60)
            logger.info("Erişim URL'leri:")
            for url in access_urls:
                logger.info(f"  → {url}")
            logger.info("=" * 60)
            app.run(host=API_HOST, port=API_PORT, debug=False, threaded=True)


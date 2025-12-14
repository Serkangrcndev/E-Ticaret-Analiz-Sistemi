import pyodbc
from config import SQL_SERVER, SQL_DATABASE, SQL_USERNAME, SQL_PASSWORD, SQL_DRIVER
import logging
import threading
from functools import lru_cache

logging.basicConfig(
    level=logging.INFO,
    format='[AKTIF] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)
# Database bağlantı loglarını sadece önemli durumlarda göster
logger.setLevel(logging.WARNING)  # INFO yerine WARNING

# Global connection pool için lock
_db_lock = threading.Lock()
_connection_pool = {}

class Database:
    def __init__(self, use_pool=True):
        # SQL Server 2022 ve ODBC Driver 18 için gerekli parametreler
        # Driver 18 TLS 1.2+ zorunlu kılar
        # Config'den gelen server adını kullan (instance adı dahil)
        server = SQL_SERVER
        
        self.connection_string = (
            f"DRIVER={{{SQL_DRIVER}}};"
            f"SERVER={server};"
            f"DATABASE={SQL_DATABASE};"
            f"UID={SQL_USERNAME};"
            f"PWD={SQL_PASSWORD};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=yes;"
            f"Connection Timeout=30"
        )
        self.conn = None
        self.use_pool = use_pool
        self.pool_key = f"{server}_{SQL_DATABASE}_{SQL_USERNAME}"
    
    def connect(self):
        try:
            # Connection pool kullan
            if self.use_pool:
                with _db_lock:
                    if self.pool_key in _connection_pool:
                        try:
                            # Mevcut bağlantıyı test et
                            conn = _connection_pool[self.pool_key]
                            cursor = conn.cursor()
                            cursor.execute("SELECT 1")
                            cursor.fetchone()
                            cursor.close()  # Cursor'ı kapat
                            self.conn = conn
                            return True
                        except:
                            # Bağlantı geçersiz, yeni bağlantı oluştur
                            try:
                                _connection_pool[self.pool_key].close()
                            except:
                                pass
                            del _connection_pool[self.pool_key]
            
            # Yeni bağlantı oluştur
            self.conn = pyodbc.connect(self.connection_string)
            
            if self.use_pool:
                with _db_lock:
                    _connection_pool[self.pool_key] = self.conn
            
            # Sadece yeni bağlantı oluşturulduğunda log (pool'dan alınan bağlantılar için log yok)
            logger.info("✓ SQL Server bağlantısı oluşturuldu")
            return True
        except Exception as e:
            logger.error(f"SQL Server bağlantı hatası: {str(e)}")
            return False
    
    def close(self, force=False):
        """
        Bağlantıyı kapat
        force=True: Pool'dan bağımsız olarak kapat
        force=False: Pool kullanılıyorsa kapatma (yeniden kullanım için)
        """
        if not self.conn:
            return
        
        if self.use_pool and not force:
            # Pool kullanılıyorsa bağlantıyı kapatma, sadece referansı temizle
            self.conn = None
            # Log yok - pool kullanımı sessiz
            return
        
        # Pool kullanılmıyorsa veya force=True ise kapat
        try:
            self.conn.close()
            if self.use_pool:
                with _db_lock:
                    if self.pool_key in _connection_pool:
                        del _connection_pool[self.pool_key]
            # Sadece gerçekten kapatıldığında log
            logger.info("✓ SQL Server bağlantısı kapatıldı")
        except Exception as e:
            logger.warning(f"Bağlantı kapatılırken hata: {str(e)}")
        finally:
            self.conn = None
    
    def create_tables(self):
        """Veritabanı tablolarını oluştur"""
        try:
            # Her işlem için ayrı cursor kullan (SQL Server'da aynı cursor üzerinde birden fazla execute sorun yaratır)
            
            # Ana site tablosu
            cursor = self.conn.cursor()
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Sites]') AND type in (N'U'))
                CREATE TABLE Sites (
                    SiteID INT PRIMARY KEY IDENTITY(1,1),
                    Domain NVARCHAR(255) UNIQUE NOT NULL,
                    SiteName NVARCHAR(255),
                    CreatedDate DATETIME DEFAULT GETDATE(),
                    LastScannedDate DATETIME,
                    RiskScore INT DEFAULT 0,
                    Status NVARCHAR(50) DEFAULT 'Active'
                )
            """)
            cursor.close()
            
            # Şikayet kayıtları
            cursor = self.conn.cursor()
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Complaints]') AND type in (N'U'))
                CREATE TABLE Complaints (
                    ComplaintID INT PRIMARY KEY IDENTITY(1,1),
                    SiteID INT FOREIGN KEY REFERENCES Sites(SiteID),
                    Source NVARCHAR(100) NOT NULL, -- 'sikayetvar', 'google', 'instagram', 'facebook'
                    Title NVARCHAR(500),
                    Content NVARCHAR(MAX),
                    Author NVARCHAR(255),
                    Date DATETIME,
                    Rating INT, -- 1-5 arası
                    Sentiment NVARCHAR(50), -- 'positive', 'negative', 'neutral'
                    URL NVARCHAR(1000),
                    IsResolved BIT DEFAULT 0, -- 0: Çözülmedi, 1: Çözüldü
                    ScrapedDate DATETIME DEFAULT GETDATE()
                )
            """)
            cursor.close()
            
            # Mevcut tabloya IsResolved sütunu ekle (eğer yoksa)
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[Complaints]') AND name = 'IsResolved')
                    BEGIN
                        ALTER TABLE Complaints ADD IsResolved BIT DEFAULT 0
                    END
                """)
                cursor.close()
            except Exception as e:
                logger.warning(f"IsResolved sütunu eklenirken uyarı: {str(e)}")
                # Sütun zaten varsa veya tablo yoksa devam et
            
            # Risk analizi sonuçları
            cursor = self.conn.cursor()
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[RiskAnalysis]') AND type in (N'U'))
                CREATE TABLE RiskAnalysis (
                    AnalysisID INT PRIMARY KEY IDENTITY(1,1),
                    SiteID INT FOREIGN KEY REFERENCES Sites(SiteID),
                    TotalComplaints INT DEFAULT 0,
                    NegativeSentimentCount INT DEFAULT 0,
                    PositiveSentimentCount INT DEFAULT 0,
                    NeutralSentimentCount INT DEFAULT 0,
                    AverageRating DECIMAL(3,2),
                    RiskLevel NVARCHAR(50), -- 'Low', 'Medium', 'High', 'Critical'
                    AnalysisDate DATETIME DEFAULT GETDATE(),
                    Details NVARCHAR(MAX) -- JSON formatında detaylar
                )
            """)
            cursor.close()
            
            # Scraping geçmişi
            cursor = self.conn.cursor()
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ScrapingHistory]') AND type in (N'U'))
                CREATE TABLE ScrapingHistory (
                    HistoryID INT PRIMARY KEY IDENTITY(1,1),
                    SiteID INT FOREIGN KEY REFERENCES Sites(SiteID),
                    Source NVARCHAR(100),
                    Status NVARCHAR(50), -- 'Success', 'Failed', 'Partial'
                    RecordsFound INT DEFAULT 0,
                    ErrorMessage NVARCHAR(MAX),
                    ScrapedDate DATETIME DEFAULT GETDATE(),
                    Duration INT -- Saniye cinsinden süre
                )
            """)
            cursor.close()
            
            self.conn.commit()
            logger.info("✓ Tablolar başarıyla oluşturuldu")
            return True
        except Exception as e:
            logger.error(f"Tablo oluşturma hatası: {str(e)}")
            try:
                self.conn.rollback()
            except:
                pass
            return False
    
    def get_or_create_site(self, domain):
        """Site'yi getir veya oluştur"""
        cursor = None
        try:
            # Önce SELECT yap
            cursor = self.conn.cursor()
            cursor.execute("SELECT SiteID FROM Sites WHERE Domain = ?", (domain,))
            row = cursor.fetchone()
            cursor.close()  # SELECT cursor'ını kapat
            
            if row:
                return row[0]
            else:
                # INSERT için yeni cursor aç
                cursor = self.conn.cursor()
                cursor.execute(
                    "INSERT INTO Sites (Domain) OUTPUT INSERTED.SiteID VALUES (?)",
                    (domain,)
                )
                site_id = cursor.fetchone()[0]
                cursor.close()
                self.conn.commit()
                return site_id
        except Exception as e:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            raise e
    
    def save_complaint(self, site_id, source, title, content, author, date, rating, sentiment, url, is_resolved=False):
        """Şikayet kaydını kaydet"""
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO Complaints 
                (SiteID, Source, Title, Content, Author, Date, Rating, Sentiment, URL, IsResolved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (site_id, source, title, content, author, date, rating, sentiment, url, 1 if is_resolved else 0))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Şikayet kaydetme hatası: {str(e)}")
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            return False
    
    def save_scraping_history(self, site_id, source, status, records_found, error_message=None, duration=None):
        """Scraping geçmişini kaydet"""
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO ScrapingHistory (SiteID, Source, Status, RecordsFound, ErrorMessage, Duration)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (site_id, source, status, records_found, error_message, duration))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Scraping geçmişi kaydetme hatası: {str(e)}")
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            return False
    
    def test_connection(self):
        """Veritabanı bağlantısını test et (hızlı test, log yok)"""
        cursor = None
        try:
            if not self.conn:
                if not self.connect():
                    return False
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            if cursor:
                cursor.close()
            return True
        except Exception as e:
            logger.debug(f"Bağlantı testi hatası: {str(e)}")
            # Cursor'ı kapat
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            # Bağlantı geçersizse yeniden dene
            try:
                if self.conn:
                    self.conn.close()
            except:
                pass
            self.conn = None
            return self.connect()
    
    def update_site_risk_score(self, site_id, risk_score):
        """Site risk skorunu güncelle"""
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE Sites 
                SET RiskScore = ?, LastScannedDate = GETDATE()
                WHERE SiteID = ?
            """, (risk_score, site_id))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Risk skoru güncelleme hatası: {str(e)}")
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            return False
    
    def migrate_add_isresolved_column(self):
        """Complaints tablosuna IsResolved sütunu ekle (migration)"""
        cursor = None
        try:
            # Önce tablonun var olup olmadığını kontrol et
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM sys.tables WHERE name = 'Complaints'
            """)
            table_exists = cursor.fetchone()[0] > 0
            cursor.close()
            
            if not table_exists:
                logger.warning("Complaints tablosu bulunamadı, önce tabloyu oluşturun")
                return False
            
            # Sütunun var olup olmadığını kontrol et
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM sys.columns 
                WHERE object_id = OBJECT_ID(N'[dbo].[Complaints]') AND name = 'IsResolved'
            """)
            column_exists = cursor.fetchone()[0] > 0
            cursor.close()
            
            if column_exists:
                logger.info("IsResolved sütunu zaten mevcut")
                return True
            
            # Sütunu ekle
            cursor = self.conn.cursor()
            cursor.execute("""
                ALTER TABLE Complaints ADD IsResolved BIT DEFAULT 0
            """)
            cursor.close()
            self.conn.commit()
            logger.info("✓ IsResolved sütunu başarıyla eklendi")
            return True
            
        except Exception as e:
            logger.error(f"IsResolved sütunu eklenirken hata: {str(e)}")
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            try:
                self.conn.rollback()
            except:
                pass
            return False


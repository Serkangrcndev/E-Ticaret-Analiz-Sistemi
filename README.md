# Site Güvenlik Analizi Projesi

Bu proje, web sitelerinin güvenlik ve itibar analizini yapmak için geliştirilmiş bir web scraping ve analiz platformudur. Farklı kaynaklardan (Şikayetvar, Trustpilot, Google Reviews) toplanan verileri analiz ederek sitelerin risk skorlarını hesaplar ve kullanıcı dostu bir arayüzle sunar.

## Özellikler

- **Çoklu Kaynak Desteği**: Şikayetvar, Trustpilot ve Google Reviews'den otomatik veri toplama
- **Risk Analizi**: Toplanan verilere göre otomatik risk skoru hesaplama
- **Sentiment Analizi**: Şikayet ve yorumların duygu analizi (pozitif/negatif/nötr)
- **Modern Web Arayüzü**: React tabanlı responsive ve kullanıcı dostu frontend
- **RESTful API**: Flask tabanlı güçlü backend API
- **Veritabanı Yönetimi**: SQL Server ile güvenli veri saklama
- **Çözümlenmiş/Çözülmemiş Takibi**: Şikayetlerin çözüm durumunu takip etme

## Teknolojiler

### Backend
- **Python 3.x**
- **Flask** - Web framework
- **SQL Server** - Veritabanı
- **Selenium** - Web scraping
- **BeautifulSoup4** - HTML parsing
- **pyodbc** - SQL Server bağlantısı

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **React Router** - Routing
- **Axios** - HTTP client

## 📋 Gereksinimler

### Backend
- Python 3.8+
- SQL Server (Express veya üzeri)
- ODBC Driver 18 for SQL Server
- Chrome/Chromium (Selenium için)

### Frontend
- Node.js 16+
- npm veya yarn

## Kurulum

### 1. Backend Kurulumu

```bash
# Proje dizinine gidin
cd backend

# Sanal ortam oluşturun (önerilir)
python -m venv venv

# Sanal ortamı aktifleştirin
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

### 2. Veritabanı Yapılandırması

1. SQL Server'ı başlatın
2. `.env` dosyası oluşturun veya `config.py` dosyasını düzenleyin:

```env
SQL_SERVER=localhost\SQLEXPRESS
SQL_DATABASE=SiteGuvenlikDB
SQL_USERNAME=sa
SQL_PASSWORD=your_password
SQL_DRIVER=ODBC Driver 18 for SQL Server
API_HOST=0.0.0.0
API_PORT=5000
DEBUG=False
```

3. Veritabanı tablolarını oluşturun:
   - API'yi başlattıktan sonra `/api/init-db` endpoint'ine POST isteği gönderin
   - Veya `create_tables.sql` dosyasını SQL Server'da çalıştırın

### 3. Frontend Kurulumu

```bash
# Frontend dizinine gidin
cd frontend

# Bağımlılıkları yükleyin
npm install
# veya
yarn install
```

### 4. API Yapılandırması

Frontend'in backend'e bağlanabilmesi için `frontend/src/services/api.js` dosyasındaki API URL'ini kontrol edin.

## Kullanım

### Backend'i Başlatma

```bash
cd backend
python app.py
```

Veya Windows'ta:
```bash
start_backend.bat
```

Backend varsayılan olarak `http://localhost:5000` adresinde çalışacaktır.

### Frontend'i Başlatma

```bash
cd frontend
npm run dev
# veya
yarn dev
```

Veya Windows'ta:
```bash
start_frontend.bat
```

Frontend varsayılan olarak `http://localhost:5173` adresinde çalışacaktır.

### Site Analizi Yapma

1. Frontend arayüzünde ana sayfaya gidin
2. Analiz etmek istediğiniz sitenin URL'sini girin
3. "Analiz Et" butonuna tıklayın
4. Analiz tamamlandığında sonuçları görüntüleyebilirsiniz

## 📡 API Endpoints

### Genel
- `GET /` - API bilgileri ve endpoint listesi
- `GET /api/health` - API sağlık kontrolü
- `GET /api/db-status` - Veritabanı bağlantı durumu

### Site İşlemleri
- `POST /api/analyze` - Site analizi başlat
  ```json
  {
    "url": "https://example.com"
  }
  ```
- `GET /api/sites` - Tüm siteleri listele
- `GET /api/site/<domain>` - Belirli bir site bilgilerini getir

### Veritabanı
- `POST /api/init-db` - Veritabanı tablolarını oluştur
- `POST /api/migrate-isresolved` - IsResolved sütunu migration

## 🗄️ Veritabanı Yapısı

### Sites Tablosu
- `SiteID` (Primary Key)
- `Domain` (Unique)
- `SiteName`
- `RiskScore` (0-100)
- `LastScannedDate`
- `CreatedDate`

### Complaints Tablosu
- `ComplaintID` (Primary Key)
- `SiteID` (Foreign Key)
- `Source` (sikayetvar, trustpilot, google_reviews)
- `Title`
- `Content`
- `Author`
- `Date`
- `Rating`
- `Sentiment` (positive, negative, neutral)
- `URL`
- `IsResolved` (boolean)

## 📁 Proje Yapısı

```
Web Scrapper new/
├── backend/
│   ├── app.py                 # Flask uygulaması
│   ├── config.py              # Yapılandırma
│   ├── database.py            # Veritabanı işlemleri
│   ├── scraper_service.py     # Scraping servisi
│   ├── requirements.txt       # Python bağımlılıkları
│   ├── create_tables.sql      # SQL tablo oluşturma scripti
│   └── scrapers/
│       ├── base_scraper.py    # Temel scraper sınıfı
│       ├── sikayetvar_scraper.py
│       ├── trustpilot_scraper.py
│       └── google_reviews_scraper.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Ana React bileşeni
│   │   ├── components/        # UI bileşenleri
│   │   ├── pages/             # Sayfa bileşenleri
│   │   ├── services/          # API servisleri
│   │   └── utils/             # Yardımcı fonksiyonlar
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## ⚙️ Yapılandırma

### Backend Yapılandırması

`backend/config.py` veya `.env` dosyası üzerinden yapılandırma yapılabilir:

- `SQL_SERVER`: SQL Server adresi ve instance
- `SQL_DATABASE`: Veritabanı adı
- `SQL_USERNAME`: Veritabanı kullanıcı adı
- `SQL_PASSWORD`: Veritabanı şifresi
- `API_HOST`: API host adresi (0.0.0.0 = tüm interface'ler)
- `API_PORT`: API port numarası
- `SCRAPING_DELAY`: İstekler arası bekleme süresi (saniye)
- `MAX_RESULTS`: Maksimum sonuç sayısı

### Frontend Yapılandırması

`frontend/src/services/api.js` dosyasında API base URL'i ayarlanabilir.

## 🔧 Geliştirme

### Yeni Scraper Ekleme

1. `backend/scrapers/base_scraper.py` sınıfından türetin
2. `scrape()` metodunu implement edin
3. `scraper_service.py` içinde yeni scraper'ı kaydedin

### Veritabanı Migration

Yeni sütun veya tablo eklemek için:
1. `database.py` içinde migration metodları ekleyin
2. `app.py` içinde migration endpoint'i oluşturun

## ⚠️ Önemli Notlar

- **Rate Limiting**: Web scraping yaparken kaynak sitelerin rate limit'lerine dikkat edin
- **Legal**: Scraping yapmadan önce hedef sitelerin kullanım şartlarını kontrol edin
- **Production**: Production ortamında Waitress veya Gunicorn gibi WSGI server'ları kullanın
- **Güvenlik**: `.env` dosyasını `.gitignore`'a ekleyin ve hassas bilgileri commit etmeyin
- **Veritabanı**: SQL Server bağlantı pool'u kullanılarak performans optimize edilmiştir

## Sorun Giderme

### Veritabanı Bağlantı Hatası
- SQL Server'ın çalıştığından emin olun
- ODBC Driver 18'in yüklü olduğunu kontrol edin
- Bağlantı bilgilerini (`config.py` veya `.env`) kontrol edin
- Firewall ayarlarını kontrol edin

### Scraping Hatası
- Chrome/Chromium'un yüklü olduğundan emin olun
- Selenium WebDriver'ın güncel olduğunu kontrol edin
- İnternet bağlantınızı kontrol edin
- Hedef sitenin erişilebilir olduğunu kontrol edin

### Frontend Bağlantı Hatası
- Backend'in çalıştığından emin olun
- CORS ayarlarını kontrol edin
- API URL'ini kontrol edin

## 📝 Lisans

Bu proje özel bir projedir.

---

**Not**: Bu proje geliştirme aşamasındadır. Production kullanımı için ek güvenlik ve optimizasyon önlemleri alınmalıdır.

<img width="1100" height="563" alt="image" src="https://github.com/user-attachments/assets/9f614336-d3d3-45c3-bfe4-46dd71b6864b" />
<img width="1916" height="943" alt="image" src="https://github.com/user-attachments/assets/20a2a2e0-734a-4c12-9ab2-7276eaa1c608" />
<img width="1912" height="940" alt="Ekran görüntüsü 2025-12-14 225135" src="https://github.com/user-attachments/assets/ceca65dc-52e7-4057-a3ea-83cf4f4bf107" />





import os
from dotenv import load_dotenv

load_dotenv()

# SQL Server Configuration
SQL_SERVER = os.getenv('SQL_SERVER', 'localhost\SQLEXPRESS')
SQL_DATABASE = os.getenv('SQL_DATABASE', '')
SQL_USERNAME = os.getenv('SQL_USERNAME', '')
SQL_PASSWORD = os.getenv('SQL_PASSWORD', '')
# SQL Server 2022 için ODBC Driver 18 önerilir
# Yüklü driver'ları kontrol etmek için: python check_odbc_drivers.py
SQL_DRIVER = os.getenv('SQL_DRIVER', 'ODBC Driver 18 for SQL Server')

# API Configuration
# 0.0.0.0 = tüm network interface'lerini dinle (tüm IP'lerden erişim)
# localhost veya 127.0.0.1 = sadece local erişim
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 5000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Scraping Configuration
SCRAPING_DELAY = int(os.getenv('SCRAPING_DELAY', 2))  # seconds between requests
MAX_RESULTS = int(os.getenv('MAX_RESULTS', 50))


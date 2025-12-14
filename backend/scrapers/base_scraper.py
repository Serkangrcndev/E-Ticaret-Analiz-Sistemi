import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class BaseScraper:
    """Tüm scraper'lar için temel sınıf - cache ve veri kaydı özelliği"""
    
    def __init__(self):
        self.delay = 1  # Sayfa istekleri arasında bekleme süresi
        self.veriler_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Veriler")
        os.makedirs(self.veriler_dir, exist_ok=True)
    
    def get_cache_path(self, domain: str, source: str) -> str:
        """Cache dosyasının yolunu oluştur"""
        clean_domain = domain.replace('.', '_').replace('/', '_').replace(':', '_')
        filename = f"{clean_domain}_{source}.txt"
        return os.path.join(self.veriler_dir, filename)
    
    def check_cache(self, domain: str, source: str) -> List[Dict]:
        """Cache'de veri varsa oku ve döndür"""
        filepath = self.get_cache_path(domain, source)
        
        if os.path.exists(filepath):
            try:
                logger.info(f"⚡ Cache'den veriler okunuyor: {filepath}")
                results = self._load_from_cache(filepath)
                # Cache'den gelen verilere işaret ekle (DB'ye kaydetme)
                for item in results:
                    item['cached'] = True
                logger.info(f"✓ Cache'den {len(results)} veri yüklendi")
                return results
            except Exception as e:
                logger.warning(f"⚠ Cache okuma hatası: {str(e)}")
                return None
        return None
    
    def save_to_cache(self, domain: str, source: str, site_name: str, results: List[Dict]):
        """Verileri txt dosyasına kaydet"""
        if not results:
            return
        
        try:
            filepath = self.get_cache_path(domain, source)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"{source.capitalize()} Verileri - {domain} ({site_name})\n")
                f.write(f"Toplam {len(results)} veri\n")
                f.write(f"{'='*60}\n\n")
                
                for idx, item in enumerate(results, 1):
                    f.write(f"[{idx}] {item.get('title', 'N/A')}\n")
                    f.write(f"Yazar: {item.get('author', 'N/A')}\n")
                    f.write(f"Tarih: {item.get('date', 'N/A')}\n")
                    f.write(f"Sentiment: {item.get('sentiment', 'N/A')}\n")
                    f.write(f"URL: {item.get('url', 'N/A')}\n")
                    f.write(f"Rating: {item.get('rating', 'N/A')}\n")
                    f.write(f"İçerik: {item.get('content', '')}\n")
                    f.write(f"{'-'*60}\n\n")
            
            logger.info(f"Veriler {filepath} dosyasına kaydedildi")
        except Exception as e:
            logger.error(f"✗ Txt dosyası kaydetme hatası: {str(e)}")
    
    def _load_from_cache(self, filepath: str) -> List[Dict]:
        """Txt dosyasından verileri yükle"""
        results = []
        current_item = {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n')
                
                # Yeni veri başlangıcı
                if line.startswith('[') and ']' in line:
                    if current_item and 'title' in current_item:
                        results.append(current_item)
                    
                    # Başlığı ayıkla
                    title = line.split('] ', 1)[1] if '] ' in line else ''
                    current_item = {'title': title, 'content': ''}
                
                # Alan ayıkla
                elif ':' in line and current_item:
                    key, value = line.split(': ', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key == 'yazar':
                        current_item['author'] = value
                    elif key == 'tarih':
                        parsed = self.parse_date(value)
                        current_item['date'] = parsed
                    elif key == 'sentiment':
                        current_item['sentiment'] = value
                    elif key == 'url':
                        current_item['url'] = value
                    elif key == 'rating':
                        try:
                            current_item['rating'] = int(value)
                        except:
                            current_item['rating'] = None
                    elif key == 'içerik':
                        current_item['content'] = value
                
                # İçerik devamı
                elif current_item and line and not line.startswith('-'):
                    if 'content' in current_item and current_item['content']:
                        current_item['content'] += '\n' + line
                    elif line and not line == '=':
                        current_item['content'] = line
        
        # Son öğeyi ekle
        if current_item and 'title' in current_item:
            results.append(current_item)
        
        return results
    
    def parse_sentiment(self, text: str) -> str:
        """Basit sentiment analizi"""
        negative_words = ['kötü', 'berbat', 'rezalet', 'sorun', 'problem', 'mağdur', 'şikayet']
        positive_words = ['iyi', 'güzel', 'teşekkür', 'memnun', 'çözüm', 'başarılı']
        
        text_lower = text.lower()
        neg_count = sum(1 for word in negative_words if word in text_lower)
        pos_count = sum(1 for word in positive_words if word in text_lower)
        
        if neg_count > pos_count:
            return 'negative'
        elif pos_count > neg_count:
            return 'positive'
        return 'neutral'
    
    def parse_date(self, date_str: str):
        """Tarih string'ini parse et"""
        from datetime import datetime
        if not date_str:
            return None
        try:
            for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%d.%m.%Y', '%d/%m/%Y']:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
            return None
        except:
            return None

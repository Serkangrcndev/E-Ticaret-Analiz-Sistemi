from scrapers.base_scraper import BaseScraper
import logging
import time
import re
from typing import List, Dict
from datetime import datetime
from urllib.parse import quote_plus
import json

# Selenium ve urllib3 uyarılarını bastır (bağlantı retry uyarıları için)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)
logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('selenium.webdriver').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

class GoogleReviewsScraper(BaseScraper):
    """Google Maps/Reviews'ten site yorumlarını çeker - Selenium kullanarak."""

    def __init__(self):
        super().__init__()
        self.delay = 3  # Selenium için daha uzun bekleme

    def get_selenium_driver(self):
        """Selenium WebDriver oluştur - webdriver-manager ile otomatik ChromeDriver yükleme"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException, NoSuchElementException
            
            # webdriver-manager ile ChromeDriver'ı otomatik indir
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
            except ImportError:
                logger.warning("webdriver-manager yüklü değil, Selenium Manager kullanılıyor")
                service = None
            
            chrome_options = Options()
            # Headless modu kapat - Google bot tespiti için
            # chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--log-level=3')  # Sadece fatal hataları göster
            chrome_options.add_argument('--silent')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            # Selenium retry mekanizmasını devre dışı bırak
            chrome_options.add_argument('--disable-background-networking')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-client-side-phishing-detection')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("detach", True)
            
            # Selenium'un retry mekanizmasını devre dışı bırakmak için
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            urllib3.disable_warnings()  # Tüm urllib3 uyarılarını kapat
            
            # Connection pool ayarları
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            if service:
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                driver = webdriver.Chrome(options=chrome_options)
            
            # Driver'ın aktif olduğunu kontrol et
            try:
                driver.current_url  # Driver'ın çalıştığını test et
            except Exception as e:
                logger.error(f"Driver başlatılamadı: {str(e)}")
                try:
                    driver.quit()
                except:
                    pass
                return None, None, None, None, None, None
            
            # Bot tespitini aşmak için script çalıştır
            try:
                driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': '''
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                        window.navigator.chrome = {
                            runtime: {}
                        };
                        Object.defineProperty(navigator, 'plugins', {
                            get: () => [1, 2, 3, 4, 5]
                        });
                    '''
                })
            except Exception as e:
                logger.debug(f"CDP komutu çalıştırılamadı: {str(e)}")
            
            return driver, By, WebDriverWait, EC, TimeoutException, NoSuchElementException
        except Exception as e:
            logger.error(f"Selenium driver oluşturulamadı: {str(e)}")
            logger.error("Chrome tarayıcı yüklü olduğundan emin olun")
            logger.error("webdriver-manager paketini yükleyin: pip install webdriver-manager")
            return None, None, None, None, None, None

    def find_google_maps_place_url(self, driver, domain: str, site_name: str):
        """Google Maps'te işletmeyi bul ve place URL'ini döndür - driver zaten açık olmalı"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        if not driver:
            return None
        
        try:
            # Google Maps'te direkt arama yap
            search_query = f"{site_name} {domain}"
            maps_search_url = f"https://www.google.com/maps/search/{quote_plus(search_query)}"
            
            logger.info(f"Google Maps'te aranıyor: {maps_search_url}")
            driver.get(maps_search_url)
            time.sleep(5)  # Sayfanın yüklenmesini bekle
            
            # İlk sonuçtaki işletmeye tıkla (genelde ilk sonuç doğru işletmedir)
            try:
                wait = WebDriverWait(driver, 10)
                
                # İşletme kartını bul ve tıkla
                place_selectors = [
                    "a[href*='/maps/place/']",
                    "div[data-result-index='0'] a",
                    "//a[contains(@href, '/maps/place/')]",
                    "div[class*='result'] a[href*='place']"
                ]
                
                place_url = None
                for selector in place_selectors:
                    try:
                        if selector.startswith("//"):
                            elements = driver.find_elements(By.XPATH, selector)
                        else:
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        if elements:
                            # İlk place linkini al
                            for elem in elements:
                                href = elem.get_attribute("href")
                                if href and "/maps/place/" in href:
                                    place_url = href
                                    logger.info(f"İşletme URL'i bulundu: {place_url}")
                                    break
                            
                            if place_url:
                                break
                    except:
                        continue
                
                # Eğer place URL bulunduysa, o sayfaya git
                if place_url:
                    driver.get(place_url)
                    time.sleep(5)
                    return place_url
                else:
                    # Place URL bulunamadı, mevcut URL'i kullan (arama sonuçları sayfası)
                    current_url = driver.current_url
                    if "/maps/place/" in current_url:
                        return current_url
                    else:
                        logger.warning("Place URL bulunamadı, arama sonuçları sayfası kullanılıyor")
                        return maps_search_url
                        
            except Exception as e:
                logger.warning(f"İşletme sayfasına gidilemedi: {str(e)}")
                # Mevcut URL'i döndür
                return driver.current_url
            
        except Exception as e:
            logger.error(f"Google Maps arama hatası: {str(e)}")
            return f"https://www.google.com/maps/search/{quote_plus(f'{site_name} {domain}')}"

    def scrape_reviews_from_maps(self, driver, maps_url: str, max_reviews: int = 30):
        """Google Maps'ten yorumları çek - driver zaten açık olmalı"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        
        if not driver:
            return []
        
        results = []
        
        try:
            # Eğer farklı bir URL'deysek, bu URL'e git
            if driver.current_url != maps_url:
                driver.get(maps_url)
                time.sleep(5)
            
            # Yorumlar sekmesine tıkla
            try:
                wait = WebDriverWait(driver, 15)
                
                # Google Maps'te yorumlar genelde tab'larda veya butonlarda
                review_tab_selectors = [
                    "button[data-tab-index='1']",  # Yorumlar sekmesi (genelde index 1)
                    "button[data-value='Yorumlar']",
                    "button[data-value='Reviews']",
                    "button[aria-label*='Yorumlar' i]",
                    "button[aria-label*='Reviews' i]",
                    "//button[contains(text(), 'Yorumlar')]",
                    "//button[contains(text(), 'Reviews')]",
                    "//button[contains(@aria-label, 'Yorumlar')]",
                    "//button[contains(@aria-label, 'Reviews')]"
                ]
                
                review_tab_clicked = False
                for selector in review_tab_selectors:
                    try:
                        if selector.startswith("//"):
                            element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        else:
                            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        
                        # Element görünür mü kontrol et
                        if element.is_displayed():
                            driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            time.sleep(1)
                            element.click()
                            review_tab_clicked = True
                            logger.info(f"Yorumlar sekmesi tıklandı ({selector})")
                            time.sleep(3)  # Yorumların yüklenmesini bekle
                            break
                    except Exception as e:
                        logger.debug(f"Selector deneniyor ({selector}): {str(e)}")
                        continue
                
                if not review_tab_clicked:
                    logger.warning("Yorumlar sekmesi bulunamadı, direkt yorumları aramaya çalışıyoruz")
                    # Belki zaten yorumlar sayfasındayız
                
            except Exception as e:
                logger.debug(f"Yorumlar sekmesi tıklanamadı: {str(e)}")
            
            # Yorumları scroll ederek yükle
            time.sleep(3)
            
            # Scroll yaparak daha fazla yorum yükle
            try:
                # Scroll container'ı bul
                scroll_containers = [
                    "div[role='main']",
                    "div[class*='scrollable']",
                    "div[class*='reviews']",
                    "div[id*='pane']"
                ]
                
                scroll_container = None
                for container_selector in scroll_containers:
                    try:
                        scroll_container = driver.find_element(By.CSS_SELECTOR, container_selector)
                        if scroll_container:
                            break
                    except:
                        continue
                
                if scroll_container:
                    # Scroll yaparak yorumları yükle
                    for i in range(5):  # 5 kez scroll yap
                        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
                        time.sleep(1)
                else:
                    # Sayfa scroll yap
                    for i in range(5):
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(1)
            except Exception as e:
                logger.debug(f"Scroll hatası: {str(e)}")
            
            time.sleep(2)
            
            # Yorumları bul - Google Maps'in güncel yapısına göre
            review_elements = []
            
            # Farklı selector'ları dene (öncelik sırasına göre)
            review_selectors = [
                ("div[data-review-id]", "CSS"),
                ("div.jftiEf", "CSS"),  # Google Maps yorum container class'ı
                ("div.MyEned", "CSS"),  # Yorum içerik container'ı
                ("//div[@data-review-id]", "XPATH"),
                ("//div[contains(@class, 'jftiEf')]", "XPATH"),
                ("//div[contains(@class, 'MyEned')]", "XPATH"),
                ("div[class*='review']", "CSS"),
                ("div[class*='comment']", "CSS")
            ]
            
            for selector, selector_type in review_selectors:
                try:
                    if selector_type == "XPATH":
                        elements = driver.find_elements(By.XPATH, selector)
                    else:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if elements and len(elements) > 0:
                        review_elements = elements
                        logger.info(f"{len(elements)} yorum elementi bulundu ({selector})")
                        break
                except Exception as e:
                    logger.debug(f"Selector hatası ({selector}): {str(e)}")
                    continue
            
            # Eğer HTML'den bulunamadıysa, script tag'lerinden JSON verilerini çıkar
            if not review_elements:
                try:
                    scripts = driver.find_elements(By.TAG_NAME, "script")
                    for script in scripts:
                        script_text = script.get_attribute("innerHTML")
                        if script_text and '"reviews"' in script_text:
                            # JSON içinde yorum verilerini bul
                            try:
                                # Basit regex ile review verilerini çıkar
                                review_pattern = r'"reviewText":\s*"([^"]+)"'
                                matches = re.findall(review_pattern, script_text)
                                
                                for i, review_text in enumerate(matches[:max_reviews]):
                                    if len(review_text) > 10:
                                        # Rating'i bul
                                        rating = None
                                        rating_pattern = r'"rating":\s*(\d+)'
                                        rating_match = re.search(rating_pattern, script_text)
                                        if rating_match:
                                            rating = int(rating_match.group(1))
                                        
                                        # Yazar adını bul
                                        author = "Google Kullanıcısı"
                                        author_pattern = r'"authorName":\s*"([^"]+)"'
                                        author_matches = re.findall(author_pattern, script_text)
                                        if author_matches and i < len(author_matches):
                                            author = author_matches[i]
                                        
                                        results.append({
                                            "title": f"Google yorumu",
                                            "content": review_text[:2000] if len(review_text) > 2000 else review_text,
                                            "author": author,
                                            "date": None,
                                            "rating": rating,
                                            "sentiment": 'positive' if rating and rating >= 4 else ('negative' if rating and rating <= 2 else 'neutral'),
                                            "url": maps_url,
                                            "is_resolved": False,
                                        })
                            except Exception as e:
                                logger.debug(f"JSON parse hatası: {str(e)}")
                except:
                    pass
            
            # HTML'den yorumları parse et
            for i, review_elem in enumerate(review_elements[:max_reviews]):
                try:
                    # Yorum metni - Google Maps'in güncel class'ları
                    content_text = ""
                    content_selectors = [
                        "span.wiI7pd",  # Ana yorum metni class'ı
                        "span.MyEned",  # Alternatif yorum metni
                        "span[class*='fontBodyMedium']",
                        "div[class*='MyEned']",
                        "span[class*='wiI7pd']"
                    ]
                    
                    for content_selector in content_selectors:
                        try:
                            content_elem = review_elem.find_element(By.CSS_SELECTOR, content_selector)
                            content_text = content_elem.text.strip()
                            if content_text and len(content_text) > 10:
                                break
                        except:
                            continue
                    
                    # Eğer hala bulunamadıysa, tüm metni al
                    if not content_text or len(content_text) < 10:
                        try:
                            # Tüm span'ları kontrol et
                            all_spans = review_elem.find_elements(By.TAG_NAME, "span")
                            for span in all_spans:
                                text = span.text.strip()
                                if text and 20 < len(text) < 1000:
                                    content_text = text
                                    break
                        except:
                            pass
                    
                    # Son çare: tüm metni al
                    if not content_text or len(content_text) < 10:
                        content_text = review_elem.text.strip()
                        # Çok uzunsa ilk paragrafı al
                        if len(content_text) > 1000:
                            lines = content_text.split('\n')
                            content_text = '\n'.join(lines[:3])  # İlk 3 satır
                    
                    if not content_text or len(content_text) < 10:
                        continue
                    
                    # Rating
                    rating = None
                    try:
                        rating_elem = review_elem.find_element(By.CSS_SELECTOR, "span[aria-label*='yıldız' i], span[aria-label*='star' i]")
                        aria_label = rating_elem.get_attribute("aria-label")
                        rating_match = re.search(r'(\d+)', aria_label)
                        if rating_match:
                            rating = int(rating_match.group(1))
                    except:
                        pass
                    
                    # Yazar
                    author = "Google Kullanıcısı"
                    try:
                        author_elem = review_elem.find_element(By.CSS_SELECTOR, "div[class*='d4r55'], div[class*='author']")
                        author = author_elem.text
                    except:
                        pass
                    
                    # Tarih
                    date_str = None
                    try:
                        date_elem = review_elem.find_element(By.CSS_SELECTOR, "span[class*='rsqaWe'], span[class*='date']")
                        date_str = date_elem.text
                    except:
                        pass
                    
                    # Sentiment
                    sentiment = self.parse_sentiment(content_text)
                    if rating:
                        if rating >= 4:
                            sentiment = 'positive'
                        elif rating <= 2:
                            sentiment = 'negative'
                    
                    results.append({
                        "title": f"Google yorumu",
                        "content": content_text[:2000] if len(content_text) > 2000 else content_text,
                        "author": author,
                        "date": self.parse_date(date_str) if date_str else None,
                        "rating": rating,
                        "sentiment": sentiment,
                        "url": maps_url,
                        "is_resolved": False,
                    })
                    
                except Exception as e:
                    logger.debug(f"Yorum parse hatası: {str(e)}")
                    continue
            
            # Daha fazla yorum yüklemek için scroll yap
            if len(results) < max_reviews:
                try:
                    # Scroll container'ı bul
                    scroll_container = driver.find_element(By.CSS_SELECTOR, "div[role='main'], div[class*='scrollable']")
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
                    time.sleep(2)
                    
                    # Yeni yorumları tekrar bul
                    new_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-review-id]")
                    if len(new_elements) > len(review_elements):
                        # Yeni yorumları parse et
                        for new_elem in new_elements[len(review_elements):max_reviews]:
                            # Aynı parse işlemini yap
                            pass
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Google Maps scraping hatası: {str(e)}")
        finally:
            # Driver'ı güvenli şekilde kapat
            try:
                if driver:
                    # Driver'ın hala aktif olduğunu kontrol et
                    try:
                        _ = driver.current_url
                        driver.quit()
                    except:
                        # Driver zaten kapanmış
                        pass
            except Exception as e:
                logger.debug(f"Driver kapatma hatası (kritik değil): {str(e)}")
        
        return results

    def scrape(self, domain: str, site_name: str) -> List[Dict]:
        """Google Reviews'ten yorumları topla; önce cache'e bak."""
        cached = self.check_cache(domain, "google_reviews")
        if cached:
            return cached

        results: List[Dict] = []

        try:
            # Selenium driver'ı aç
            driver, By, WebDriverWait, EC, TimeoutException, NoSuchElementException = self.get_selenium_driver()
            if not driver:
                logger.error("Selenium driver oluşturulamadı")
                return results
            
            try:
                # Google Maps'te işletmeyi bul
                logger.info(f"Google Maps'te işletme aranıyor: {site_name} {domain}")
                maps_url = self.find_google_maps_place_url(driver, domain, site_name)
                
                if not maps_url:
                    logger.warning("Google Maps işletme URL'i bulunamadı")
                    return results
                
                logger.info(f"Google Maps işletme URL'i bulundu: {maps_url}")
                
                # Yorumları çek (driver zaten açık)
                results = self.scrape_reviews_from_maps(driver, maps_url, max_reviews=30)
                
                logger.info(f"✓ Google Reviews'ten {len(results)} yorum bulundu")
                self.save_to_cache(domain, "google_reviews", site_name, results)
                return results
                
            finally:
                # Driver'ı güvenli şekilde kapat
                try:
                    if driver:
                        # Driver'ın hala aktif olduğunu kontrol et
                        try:
                            _ = driver.current_url
                            driver.quit()
                        except:
                            # Driver zaten kapanmış veya bağlantı kopmuş
                            logger.debug("Driver zaten kapanmış veya bağlantı kopmuş (kritik değil)")
                            pass
                except Exception as e:
                    logger.debug(f"Driver kapatma hatası (kritik değil): {str(e)}")

        except Exception as e:
            logger.error(f"✗ Google Reviews scraping hatası: {str(e)}")
            return results


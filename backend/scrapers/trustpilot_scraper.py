from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
import logging
import time
import re
import requests
from typing import List, Dict
from datetime import datetime
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

class TrustpilotScraper(BaseScraper):
    """Trustpilot'tan şirket yorumlarını çeker."""

    def __init__(self):
        super().__init__()
        self.delay = 2

    def scrape(self, domain: str, site_name: str) -> List[Dict]:
        """Trustpilot'tan yorumları topla; önce cache'e bak."""
        cached = self.check_cache(domain, "trustpilot")
        if cached:
            return cached

        results: List[Dict] = []
        max_pages = 3

        # Trustpilot'ta şirket araması
        search_terms = [
            site_name,
            domain.split(".")[0],
            domain.replace(".com", "").replace(".net", "").replace(".org", "")
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        try:
            for term in search_terms:
                if not term or len(term) < 3:
                    continue

                # Trustpilot şirket arama URL'i
                search_url = f"https://www.trustpilot.com/review/{quote_plus(term)}.com.tr"
                
                # Önce .com.tr ile dene, sonra .com
                urls_to_try = [
                    f"https://www.trustpilot.com/review/{quote_plus(term)}.com.tr",
                    f"https://www.trustpilot.com/review/{quote_plus(term)}.com",
                    f"https://www.trustpilot.com/review/{quote_plus(term)}",
                    f"https://tr.trustpilot.com/review/{quote_plus(term)}.com.tr"
                ]
                
                found_results = False
                
                for search_url in urls_to_try:
                    try:
                        resp = requests.get(search_url, headers=headers, timeout=10)
                        if resp.status_code != 200:
                            continue

                        soup = BeautifulSoup(resp.text, "html.parser")
                        
                        # Trustpilot yorum yapısı
                        reviews = soup.find_all("article", class_=re.compile(r"review|card", re.I))
                        
                        if not reviews:
                            # Alternatif yapı
                            reviews = soup.find_all("div", {"data-review-id": True})
                        
                        if not reviews:
                            # Başka bir yapı dene
                            reviews = soup.find_all("section", class_=re.compile(r"review", re.I))
                        
                        if not reviews:
                            continue
                        
                        for review in reviews[:20]:  # İlk 20 yorum
                            try:
                                # Yorum metni
                                content_elem = review.find("p", class_=re.compile(r"review|text|body", re.I))
                                if not content_elem:
                                    content_elem = review.find("div", class_=re.compile(r"review-text|content", re.I))
                                
                                if not content_elem:
                                    # Tüm paragrafları al
                                    paragraphs = review.find_all("p")
                                    if paragraphs:
                                        content_elem = paragraphs[0]
                                
                                content = ""
                                if content_elem:
                                    content = content_elem.get_text(strip=True)
                                
                                if not content or len(content) < 10:
                                    continue
                                
                                # Başlık
                                title_elem = review.find("h2") or review.find("h3") or review.find("a", class_=re.compile(r"title", re.I))
                                title = ""
                                if title_elem:
                                    title = title_elem.get_text(strip=True)
                                
                                if not title:
                                    title = f"{term} Trustpilot yorumu"
                                
                                # Yazar
                                author_elem = review.find("span", class_=re.compile(r"author|consumer|user", re.I))
                                if not author_elem:
                                    author_elem = review.find("div", class_=re.compile(r"consumer", re.I))
                                
                                author = "Trustpilot Kullanıcısı"
                                if author_elem:
                                    author_text = author_elem.get_text(strip=True)
                                    if author_text:
                                        author = author_text
                                
                                # Tarih
                                date_elem = review.find("time") or review.find("span", class_=re.compile(r"date|published", re.I))
                                date_str = None
                                if date_elem:
                                    date_str = date_elem.get("datetime") or date_elem.get("title") or date_elem.get_text(strip=True)
                                
                                # Rating (Trustpilot 5 yıldız sistemi)
                                rating = None
                                rating_elem = review.find("div", class_=re.compile(r"star|rating", re.I))
                                if rating_elem:
                                    # Yıldız sayısını bul
                                    stars = rating_elem.find_all("img", alt=re.compile(r"star|yıldız", re.I))
                                    if not stars:
                                        stars = rating_elem.find_all("span", class_=re.compile(r"star", re.I))
                                    
                                    if stars:
                                        rating = len([s for s in stars if "filled" in str(s.get("class", [])) or "active" in str(s.get("class", []))])
                                
                                # Eğer rating bulunamadıysa, data attribute'dan dene
                                if not rating:
                                    rating_attr = review.get("data-review-rating") or review.get("data-rating")
                                    if rating_attr:
                                        try:
                                            rating = int(rating_attr)
                                        except:
                                            pass
                                
                                # URL
                                review_url = search_url
                                review_link = review.find("a", href=re.compile(r"/review/", re.I))
                                if review_link:
                                    href = review_link.get("href")
                                    if href.startswith("/"):
                                        review_url = f"https://www.trustpilot.com{href}"
                                    elif href.startswith("http"):
                                        review_url = href
                                
                                # Sentiment analizi
                                full_text = f"{title} {content}"
                                sentiment = self.parse_sentiment(full_text)
                                
                                # Rating'e göre sentiment düzelt
                                if rating:
                                    if rating >= 4:
                                        sentiment = 'positive'
                                    elif rating <= 2:
                                        sentiment = 'negative'
                                
                                parsed_date = self.parse_date(date_str) if date_str else None
                                
                                # Çözülmüş durumu (Trustpilot'ta şirket yanıtı varsa çözülmüş sayılabilir)
                                is_resolved = False
                                company_response = review.find("div", class_=re.compile(r"company|response|reply", re.I))
                                if company_response:
                                    is_resolved = True
                                
                                results.append({
                                    "title": title,
                                    "content": content[:2000] if len(content) > 2000 else content,
                                    "author": author,
                                    "date": parsed_date,
                                    "rating": rating,
                                    "sentiment": sentiment,
                                    "url": review_url,
                                    "is_resolved": is_resolved,
                                })
                                
                                found_results = True
                                
                            except Exception as e:
                                logger.debug(f"Yorum parse hatası: {str(e)}")
                                continue
                        
                        if found_results:
                            break
                        
                        time.sleep(self.delay)
                        
                    except Exception as e:
                        logger.debug(f"Trustpilot URL denemesi hatası ({search_url}): {str(e)}")
                        continue
                
                if found_results:
                    logger.info(f"✓ Trustpilot'tan {len(results)} yorum bulundu (terim: {term})")
                    break

            logger.info(f"✓ Trustpilot'tan toplam {len(results)} yorum bulundu")
            self.save_to_cache(domain, "trustpilot", site_name, results)
            return results

        except Exception as e:
            logger.error(f"✗ Trustpilot scraping hatası: {str(e)}")
            return results


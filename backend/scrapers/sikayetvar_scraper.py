from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
import logging
import time
import re
import os
from urllib.parse import quote_plus
import requests
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class SikayetvarScraper(BaseScraper):
    """Şikayetvar'dan site hakkında şikayetleri çeker."""

    def __init__(self):
        super().__init__()

    def to_url_slug(self, name: str) -> str:
        """Türkçe karakterleri ve boşlukları URL uyumlu hale getir."""
        tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
        name = name.translate(tr_map)
        name = name.replace(" ", "-")
        name = name.lower()
        name = re.sub(r"[^a-z0-9\-]", "", name)
        return name

    def scrape(self, domain: str, site_name: str) -> List[Dict]:
        """Şikayetvar'dan şikayetleri topla; önce cache'e bak."""
        cached = self.check_cache(domain, "sikayetvar")
        if cached:
            return cached

        results: List[Dict] = []
        max_pages = 5

        company_slug = self.to_url_slug(site_name)
        domain_slug = self.to_url_slug(domain.split(".")[0])
        search_terms = [company_slug, domain_slug]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            for company in search_terms:
                if not company:
                    continue

                base_url = f"https://www.sikayetvar.com/{company}"
                found_results = False

                for page in range(1, max_pages + 1):
                    try:
                        url = base_url if page == 1 else f"{base_url}?page={page}"
                        resp = requests.get(url, headers=headers)
                        if resp.status_code != 200:
                            break

                        soup = BeautifulSoup(resp.text, "html.parser")
                        articles = soup.find_all("article", class_="card-v2")
                        if not articles:
                            break

                        found_results = True

                        for article in articles:
                            h2 = article.find("h2", class_="complaint-title")
                            a = h2.find("a") if h2 else None
                            title = a.get_text(strip=True) if a else ""
                            if not title:
                                continue

                            desc = ""
                            section = article.find("section")
                            if section:
                                p = section.find("p", class_="complaint-description js-replace-to-link")
                                if not p:
                                    for p_tag in section.find_all("p"):
                                        classes = p_tag.get("class", [])
                                        if "complaint-description" in classes and "js-replace-to-link" in classes:
                                            p = p_tag
                                            break
                                if p:
                                    desc = p.get_text(strip=True)

                            author_elem = article.find("a", class_=re.compile(r"user|author|writer"))
                            author = author_elem.get_text(strip=True) if author_elem else "Şikayetvar Kullanıcısı"

                            date_elem = article.find("time") or article.find("span", class_=re.compile(r"date|time"))
                            date_str = None
                            if date_elem:
                                date_str = date_elem.get("datetime") or date_elem.get("title") or date_elem.get_text(strip=True)

                            url_link = base_url
                            if a and a.get("href"):
                                href = a.get("href")
                                if href.startswith("/"):
                                    url_link = f"https://www.sikayetvar.com{href}"
                                elif href.startswith("http"):
                                    url_link = href

                            full_text = f"{title} {desc}"
                            sentiment = self.parse_sentiment(full_text)
                            parsed_date = self.parse_date(date_str) if date_str else None
                            
                            # Çözülmüş durumu tespit et
                            is_resolved = False
                            # Şikayetvar'da çözülmüş şikayetler genellikle badge veya özel class ile işaretlenir
                            resolved_badge = article.find("span", class_=re.compile(r"resolved|cozuldu|solved|success", re.I))
                            resolved_text = article.find(string=re.compile(r"çözüldü|cozuldu|resolved|solved", re.I))
                            if resolved_badge or resolved_text:
                                is_resolved = True
                            
                            # Başlık veya içerikte çözüldü ifadesi var mı kontrol et
                            if not is_resolved:
                                resolved_keywords = ["çözüldü", "cozuldu", "resolved", "solved", "yanıtlandı", "cevaplandı"]
                                full_text_lower = full_text.lower()
                                if any(keyword in full_text_lower for keyword in resolved_keywords):
                                    # Ancak sadece "çözülmedi" gibi negatif ifadeleri hariç tut
                                    if "çözülmedi" not in full_text_lower and "cozulmedi" not in full_text_lower:
                                        is_resolved = True

                            results.append(
                                {
                                    "title": title,
                                    "content": desc[:2000] if len(desc) > 2000 else desc,
                                    "author": author,
                                    "date": parsed_date,  # datetime veya None
                                    "rating": None,
                                    "sentiment": sentiment,
                                    "url": url_link,
                                    "is_resolved": is_resolved,
                                }
                            )

                        time.sleep(self.delay)

                    except Exception as e:
                        logger.warning(f"Şikayetvar sayfa hatası (sayfa {page}): {str(e)}")
                        break

                if found_results and results:
                    break

            logger.info(f"✓ Şikayetvar'dan {len(results)} şikayet bulundu")
            self.save_to_cache(domain, "sikayetvar", site_name, results)
            return results

        except Exception as e:
            logger.error(f"✗ Şikayetvar scraping hatası: {str(e)}")
            return results


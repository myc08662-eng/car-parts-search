import re
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
import time
from httpx import Client, Timeout, ConnectError
import json

logger = logging.getLogger(__name__)

ALLOWED_DOMAINS = {
    'ozon.ru', 'tachka.ru', 'trialli.ru', 'shop.polosedan.ru',
    'mobiland.auto', 'amag.ru', 'startvolt.com', 'baza.drom.ru',
    'v-avto.ru', 'autone.ru', 'koleso.ru', 'zapkorea.ru',
    'luzar.ru', 'carvilleshop.ru', 'ruli.ru', 'cars.marshall.parts'
}

def parse_price(url: str) -> float | None:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    if domain.startswith('www.'):
        domain = domain[4:]
    
    if not any(domain.endswith(allowed) for allowed in ALLOWED_DOMAINS):
        logger.warning(f"Домен {domain} не в белом списке")
        return None

    try:
        headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                 #'Accept-Encoding': 'gzip, deflate, br',
                 'Connection': 'keep-alive',
                 'Referer': 'https://www.google.com/',
                 'Sec-Fetch-Dest': 'document',
                 'Sec-Fetch-Mode': 'navigate',
                 'Sec-Fetch-Site': 'none',
                 'Sec-Fetch-User': '?1',
                 'Upgrade-Insecure-Requests': '1',
                }
        max_retries = 3
        response = None
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                    response = client.get(url, headers=headers)
                break
            except (httpx.ConnectError, httpx.TimeoutException, httpx.ReadTimeout) as e:
                if attempt == max_retries - 1:
                    logger.error(f"Не удалось загрузить страницу после {max_retries} попыток: {url} – {e}")
                    return None
                wait = 2 ** attempt
                logger.warning(f"Попытка {attempt+1} не удалась для {url}, повтор через {wait}с: {e}")
                time.sleep(wait)
        
        if response is None or response.status_code != 200:
            logger.warning(f"Не удалось получить страницу: {url}, статус {response.status_code if response else 'нет ответа'}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        json_ld = soup.select_one('script[type="application/ld+json"]')
        if json_ld:
            try:
                data = json.loads(json_ld.string)
                # Ищем цену в offers.price
                if 'offers' in data and isinstance(data['offers'], dict):
                    price = data['offers'].get('price')
                    if price is not None:
                        try:
                            price = float(price)
                            if 50 <= price <= 1000000:
                                return round(price, 2)
                        except (ValueError, TypeError):
                            pass
                # Если offers – список (бывает), перебираем
                elif 'offers' in data and isinstance(data['offers'], list):
                    for offer in data['offers']:
                        if 'price' in offer:
                            try:
                                price = float(offer['price'])
                                if 50 <= price <= 1000000:
                                    return round(price, 2)
                            except (ValueError, TypeError):
                                continue
            except (json.JSONDecodeError, AttributeError, KeyError):
                pass

        # Отдельная проверка для tachka.ru
        buy_box = soup.select_one('[data-buy-box]')
        if buy_box and buy_box.get('data-price'):
            price_text = buy_box['data-price']
            cleaned = re.sub(r'[^\d,.]', '', price_text.replace(' ', ''))
            if cleaned:
                cleaned = cleaned.replace(',', '.')
                parts = cleaned.split('.')
                if len(parts) > 2:
                    cleaned = ''.join(parts[:-1]) + '.' + parts[-1]
                try:
                    price = float(cleaned)
                    if 50 <= price <= 1000000:
                        return round(price, 2)
                except ValueError:
                    pass

        # Список селекторов для поиска цены
        price_selectors = [
            'span.only_price',
            'div.panel-price__price__value',
            'div.section-price__price__new',
            'span.c-product-management__price',
            'meta[property="product:price:amount"]',
            'p.product-main-order__pickup-discount-price',
            '[itemprop="price"]',
            'p.product-main-order__price',
            'span.font-display',
            'span.flex.items-baseline.gap-2\\.5.mb-4',
            '.price', '.product-price', '.cost', '.current-price',
            '[data-price]', '.price__current', '.price_value',
            '.item-price', '.price-block__price', '.price--red',
            '.js-price', '.product__price'
        ]
        price_text = None
        for selector in price_selectors:
            elem = soup.select_one(selector)
            if elem:
                price_text = elem.get_text(strip=True)
                break

        if not price_text:
            elem_with_data = soup.find(attrs={'data-price': True})
            if elem_with_data:
                price_text = elem_with_data['data-price']
            else:
                for elem in soup.find_all(['span', 'div', 'meta']):
                    text = elem.get_text(strip=True)
                    if re.search(r'\d+\s*[\.,]?\s*\d*\s*[₽руб]', text):
                        price_text = text
                        break

        if not price_text:
            return None

        cleaned = re.sub(r'[^\d,.]', '', price_text.replace(' ', ''))
        if not cleaned:
            return None

        cleaned = cleaned.replace(',', '.')
        parts = cleaned.split('.')
        if len(parts) > 2:
            cleaned = ''.join(parts[:-1]) + '.' + parts[-1]

        try:
            price = float(cleaned)
            if price < 1 or price > 1000000:
                return None
            return round(price, 2)
        except ValueError:
            return None

    except httpx.TimeoutException:
        logger.warning(f"Таймаут при запросе {url}")
        return None
    except Exception as e:
        logger.exception(f"Ошибка парсинга {url}: {e}")
        return None
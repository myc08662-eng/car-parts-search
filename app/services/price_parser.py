import re
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging

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
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            headers = {'User-Agent': 'Mozilla/5.0 ...'}
            response = client.get(url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"Не удалось получить страницу: {url}, статус {response.status_code}")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            #Отдельная проверка для tachka.ru
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
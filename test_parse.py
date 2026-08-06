import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.price_parser import parse_price
import httpx
from bs4 import BeautifulSoup

url = "https://barnaul.koleso.ru/catalog/product/filtron-filtr-vozdushnyiy-ap-122-8-hyundai-solaris--kia-rio-1-6i-11/"

headers = {
    'User-Agent': 'Mozilla/5.0 ...',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Referer': 'https://www.google.com/',
}
with httpx.Client(timeout=15.0, follow_redirects=True) as client:
    response = client.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    meta = soup.select_one('meta[property="product:price:amount"]')
    if meta:
        print(f"Мета-тег найден, content={meta.get('content')}")
    else:
        print("Мета-тег не найден")
    span = soup.select_one('span.c-product-management__price')
    div_price = soup.select_one('div.section-price__price__new')
    if div_price:
        print(f"Div с ценой найден, текст={div_price.get_text(strip=True)}")
    else:
        print("Div с ценой не найден")
    if span:
        print(f"Span найден, текст={span.get_text(strip=True)}")
    else:
        print("Span не найден")
    json_ld = soup.select_one('script[type="application/ld+json"]')
    if json_ld:
        print("JSON-LD найден")
        import json
        try:
            data = json.loads(json_ld.string)
            price_from_json = data.get('offers', {}).get('price')
            print(f"Цена из JSON-LD: {price_from_json}")
        except Exception as e:
            print(f"Ошибка парсинга JSON-LD: {e}")
    else:
        print("JSON-LD не найден")
    only_price = soup.select_one('span.only_price')
    if only_price:
        print(f"Span с only_price найден, текст={only_price.get_text(strip=True)}")
    else:
        print("Span с only_price не найден")
    price_vavto = soup.select_one('span.Price_value__IsrEW')
    if price_vavto:
        print(f"Span с Price_value__IsrEW найден, текст={price_vavto.get_text(strip=True)}")
    else:
        print("Span с Price_value__IsrEW не найден")

price = parse_price(url)
print(f"Распарсенная цена: {price}")
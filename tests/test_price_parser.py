import pytest
from app.services.price_parser import parse_price

def test_parse_price_amag(mocker):
    mock_html = """
    <meta itemprop="price" content="1737">
    <p class="product-main-order__price">1 737 ₽</p>
    """
    mock_get = mocker.patch('httpx.Client.get')
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.text = mock_html
    mock_get.return_value = mock_response

    url = "https://www.amag.ru/catalog/..."
    price = parse_price(url)
    assert price == 1737.0

def test_parse_price_tachka(mocker):
    mock_html = """
    <div data-buy-box data-price="2365">
        <span class="font-display">2 365 ₽</span>
    </div>
    """
    mock_get = mocker.patch('httpx.Client.get')
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.text = mock_html
    mock_get.return_value = mock_response

    url = "https://tachka.ru/..."
    price = parse_price(url)
    assert price == 2365.0

def test_parse_price_not_found(mocker):
    mock_html = "<html><body>Нет цены</body></html>"
    mock_get = mocker.patch('httpx.Client.get')
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.text = mock_html
    mock_get.return_value = mock_response

    url = "https://example.com/..."
    price = parse_price(url)
    assert price is None

def test_parse_price_http_error(mocker):
    mock_get = mocker.patch('httpx.Client.get')
    mock_response = mocker.MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    url = "https://example.com/..."
    price = parse_price(url)
    assert price is None
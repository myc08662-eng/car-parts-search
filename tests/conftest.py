import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db_connection
from app.services.tfidf_search import TFIDFSearch
from app.services import search_service

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_db_connection(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mocker.patch('app.repositories.category_repo.get_db_connection', return_value=mock_conn)
    return mock_conn, mock_cursor

@pytest.fixture
def mock_search_engine(mocker):
    mock_engine = mocker.MagicMock(spec=TFIDFSearch)
    mock_engine.is_fitted = True
    mock_engine.search_by_category.return_value = [
        {
            "part_id": 1,
            "car_id": 1,
            "part_name": "Масляный фильтр",
            "car_name": "Toyota Corolla E150",
            "category": "Фильтры",
            "price": 650,
            "original_price": 650,
            "parsed_price": None,
            "url": "https://example.com",
            "vendor": "Ozon",
            "similarity": 0.9
        }
    ]
    mocker.patch('app.services.search_service.search_engine', mock_engine)
    return mock_engine
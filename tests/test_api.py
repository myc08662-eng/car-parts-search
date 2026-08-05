import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_home_page(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "Поиск автозапчастей" in response.text

def test_categories_endpoint(client: TestClient, mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        {"id": 1, "name": "Фильтры"},
        {"id": 2, "name": "ГРМ"}
    ]
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name"] == "Фильтры"

def test_search_ai(client: TestClient, mock_search_engine):
    response = client.get("/api/search/ai?q=масляный")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["results"][0]["part_name"] == "Масляный фильтр"

def test_search_ai_empty_query(client: TestClient):
    response = client.get("/api/search/ai?q=")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0

def test_instructions_page(client: TestClient, mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.side_effect = [
        {"brand": "Toyota", "model": "Corolla", "generation": "E150"},
        None  
    ]
    mock_cursor.fetchall.return_value = []  
    response = client.get("/instructions/1")
    assert response.status_code == 200
    assert "Toyota Corolla E150" in response.text
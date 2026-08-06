import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_search_query_length_limit():
    long_query = 'a' * 300
    response = client.get(f"/api/search/ai?q={long_query}")
    assert response.status_code == 200
    data = response.json()
    assert data['count'] == 0  # или другое поведение

def test_special_characters_escaping():
    response = client.get("/api/search/ai?q=<script>alert(1)</script>")
    assert response.status_code == 200
    data = response.json()
    for item in data.get('results', []):
        part_name = item.get('part_name', '')
        assert '<script>' not in part_name
        assert 'alert' not in part_name
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.benchmark
def test_search_performance(benchmark):
    def do_search():
        response = client.get("/api/search/ai?q=масляный")
        assert response.status_code == 200
    benchmark(do_search)

def test_multiple_requests():
    import time
    start = time.time()
    for _ in range(20):
        response = client.get("/api/search/ai?q=тест")
        assert response.status_code == 200
    elapsed = time.time() - start
    assert elapsed < 5.0, f"20 запросов заняли {elapsed} секунд, что больше 5"
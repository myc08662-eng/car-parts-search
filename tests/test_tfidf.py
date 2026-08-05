import pytest
from app.services.tfidf_search import TFIDFSearch

def test_tfidf_fit_and_search():
    parts_data = [
        {"part_id": 1, "part_name": "Масляный фильтр", "car_name": "Toyota Corolla", "category": "Фильтры"},
        {"part_id": 2, "part_name": "Воздушный фильтр", "car_name": "Renault Logan", "category": "Фильтры"},
        {"part_id": 3, "part_name": "Ремень ГРМ", "car_name": "Volkswagen Polo", "category": "ГРМ"},
    ]
    searcher = TFIDFSearch()
    searcher.fit(parts_data)
    
    results = searcher.search_by_category("масляный", top_k=2)
    assert len(results) == 1  
    assert results[0]["part_name"] == "Масляный фильтр"
    
    results = searcher.search_by_category("фильтр", top_k=3)
    assert len(results) == 2  
    assert results[0]["category"] == "Фильтры"
    assert results[1]["category"] == "Фильтры"
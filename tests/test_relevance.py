import pytest
from app.services.tfidf_search import TFIDFSearch

TEST_PARTS = [
    {"part_id": 1, "part_name": "Масляный фильтр", "car_name": "Toyota Corolla E150", "category": "Фильтры", "price": 650, "url": "https://example.com/1", "vendor": "Ozon"},
    {"part_id": 2, "part_name": "Воздушный фильтр", "car_name": "Renault Logan 2", "category": "Фильтры", "price": 800, "url": "https://example.com/2", "vendor": "Ozon"},
    {"part_id": 3, "part_name": "Ремень ГРМ", "car_name": "Volkswagen Polo Sedan", "category": "ГРМ", "price": 12000, "url": "https://example.com/3", "vendor": "Trialli"},
    {"part_id": 4, "part_name": "Фильтр масляный", "car_name": "Kia Rio 3", "category": "Фильтры", "price": 400, "url": "https://example.com/4", "vendor": "Tachka"},
]

@pytest.fixture
def mock_parts_repo(mocker):
    """Мокает part_repo.get_all_parts_with_links, возвращая TEST_PARTS"""
    mock = mocker.patch('app.repositories.part_repo.get_all_parts_with_links')
    mock.return_value = TEST_PARTS
    return mock

def test_relevance_maslyany_filtr(mock_parts_repo):
    """Поиск 'масляный фильтр' должен находить оба масляных фильтра"""
    searcher = TFIDFSearch()
    parts = mock_parts_repo()  
    searcher.fit(parts)
    
    results = searcher.search_by_category("масляный фильтр", top_k=3)
    part_names = [r['part_name'] for r in results]
    assert any('Масляный' in name or 'масляный' in name for name in part_names[:2])
    expected = {'Масляный фильтр', 'Фильтр масляный'}
    found = {r['part_name'] for r in results[:2]}
    assert len(found.intersection(expected)) >= 2

def test_relevance_remen(mock_parts_repo):
    """Поиск 'ремень' должен находить 'Ремень ГРМ'"""
    searcher = TFIDFSearch()
    searcher.fit(mock_parts_repo())
    
    results = searcher.search_by_category("ремень", top_k=3)
    part_names = [r['part_name'] for r in results]
    assert any('Ремень' in name for name in part_names[:1])

def test_relevance_filter_category(mock_parts_repo):
    """Поиск 'фильтр' с фильтрацией по категории 'Фильтры' должен возвращать только фильтры"""
    searcher = TFIDFSearch()
    searcher.fit(mock_parts_repo())
    
    results = searcher.search_by_category("фильтр", category="Фильтры", top_k=3)
    categories = [r['category'] for r in results]
    assert all(cat == "Фильтры" for cat in categories)
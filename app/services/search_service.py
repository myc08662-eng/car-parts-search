from app.repositories import part_repo   
from app.services.tfidf_search import TFIDFSearch

search_engine = TFIDFSearch()

def init_search_engine():
    """Вызывается при старте приложения"""
    parts = part_repo.get_all_parts_with_links()
    if parts:
        search_engine.fit(parts)
    return search_engine.is_fitted

def search_parts(query: str, category: str = None):
    return search_engine.search_by_category(query, category)
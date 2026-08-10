from app.repositories import part_repo   
from app.services.tfidf_search import TFIDFSearch

search_engine = TFIDFSearch()

def init_search_engine():
    parts = part_repo.get_all_parts_with_links()
    if parts:
        search_engine.fit(parts)
    return search_engine.is_fitted

def search_parts(query: str, category: str = None, top_k: int = 30):
    return search_engine.search_by_category(query, category, top_k=top_k)
from fastapi import APIRouter, Request, HTTPException
from app.services import search_service
from app.repositories import part_repo
from app.config import get_settings

router = APIRouter(prefix="/api/search", tags=["search"])
settings = get_settings()

@router.get("")
async def simple_search(q: str = ""):
    if len(q) < settings.SEARCH_MIN_QUERY_LEN:
        return {"results": [], "count": 0}
    
    if not search_service.search_engine.is_fitted:
        results = part_repo.search_by_sql_like(q)
        return {"results": results, "count": len(results), "fallback": True}
    
    results = search_service.search_parts(q, category=None)
    return {"results": results, "count": len(results)}

@router.get("/ai")
async def ai_search(q: str = "", category: str = ""):
    if len(q) < settings.SEARCH_MIN_QUERY_LEN:
        return {"results": [], "count": 0}
    
    if not search_service.search_engine.is_fitted:
        results = part_repo.search_by_sql_like(q)
        if category:
            results = [r for r in results if r.get('category', '').lower() == category.lower()]
        return {"results": results[:30], "count": len(results), "fallback": True}
    
    results = search_service.search_parts(q, category if category else None)
    return {
        "results": results,
        "count": len(results),
        "query": q,
        "category": category or "все"
    }
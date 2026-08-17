from fastapi import APIRouter, Request, HTTPException
from app.services import search_service
from app.repositories import part_repo
from app.config import get_settings

router = APIRouter(prefix="/api/search", tags=["search"])
settings = get_settings()

@router.get("/ai")
async def ai_search(q: str = "", category: str = "", page: int = 1, limit: int = 20):
    if len(q) < settings.SEARCH_MIN_QUERY_LEN or len(q) > settings.SEARCH_MAX_QUERY_LEN:
        return {"results": [], "count": 0, "page": page, "limit": limit, "total_pages": 0}
    
    if not search_service.search_engine.is_fitted:
        results = part_repo.search_by_sql_like(q)
        if category:
            results = [r for r in results if r.get('category', '').lower() == category.lower()]
        total = len(results)
        start = (page - 1) * limit
        end = start + limit
        paginated = results[start:end]
        return {
            "results": paginated,
            "count": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit,
            "fallback": True,
            "query": q,
            "category": category or "все"
        }
    
    top_k_needed = limit * page + limit  
    all_results = search_service.search_parts(q, category if category else None, top_k=top_k_needed)
    total = len(all_results)
    start = (page - 1) * limit
    end = start + limit
    paginated = all_results[start:end]
    return {
        "results": paginated,
        "count": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "query": q,
        "category": category or "все"
    }

@router.get("")
async def simple_search(q: str = "", page: int = 1, limit: int = 20):
    if len(q) < settings.SEARCH_MIN_QUERY_LEN or len(q) > settings.SEARCH_MAX_QUERY_LEN:
        return {"results": [], "count": 0, "page": page, "limit": limit, "total_pages": 0}
    
    if not search_service.search_engine.is_fitted:
        results = part_repo.search_by_sql_like(q)  # без limit
        total = len(results)
        start = (page - 1) * limit
        end = start + limit
        paginated = results[start:end]
        return {
            "results": paginated,
            "count": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit,
            "fallback": True
        }

    top_k_needed = limit * page + limit
    all_results = search_service.search_parts(q, category=None, top_k=top_k_needed)
    total = len(all_results)
    start = (page - 1) * limit
    end = start + limit
    paginated = all_results[start:end]
    return {
        "results": paginated,
        "count": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }
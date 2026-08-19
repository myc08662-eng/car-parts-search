from fastapi import APIRouter, Request, HTTPException
from app.services import search_service
from app.repositories import part_repo
from app.config import get_settings
from app.services.cache import search_cache

router = APIRouter(prefix="/api/search", tags=["search"])
settings = get_settings()

@router.get("/ai")
async def ai_search(q: str = "", category: str = "", page: int = 1, limit: int = 20):
    if len(q) < settings.SEARCH_MIN_QUERY_LEN or len(q) > settings.SEARCH_MAX_QUERY_LEN:
        return {"results": [], "count": 0, "page": page, "limit": limit, "total_pages": 0}

    # Кэш
    cache_key = f"ai_{q}_{category}_{page}_{limit}"
    cached = search_cache.get(cache_key)
    if cached is not None:
        return cached

    if not search_service.search_engine.is_fitted:
        offset = (page - 1) * limit
        total = part_repo.count_search_results(q, category if category else None)
        results = part_repo.search_by_sql_like(q, category if category else None, offset=offset, limit=limit)
        paginated = results
        response_data = {
            "results": paginated,
            "count": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit,
            "fallback": True,
            "query": q,
            "category": category or "все"
        }
        search_cache.set(cache_key, response_data)
        return response_data

    top_k_needed = limit * page + limit
    all_results = search_service.search_parts(q, category if category else None, top_k=top_k_needed)
    total = len(all_results)
    start = (page - 1) * limit
    end = start + limit
    paginated = all_results[start:end]
    response_data = {
        "results": paginated,
        "count": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "query": q,
        "category": category or "все"
    }
    search_cache.set(cache_key, response_data)
    return response_data


@router.get("")
async def simple_search(q: str = "", page: int = 1, limit: int = 20):
    if len(q) < settings.SEARCH_MIN_QUERY_LEN or len(q) > settings.SEARCH_MAX_QUERY_LEN:
        return {"results": [], "count": 0, "page": page, "limit": limit, "total_pages": 0}

    # Кэш
    cache_key = f"simple_{q}_{page}_{limit}"
    cached = search_cache.get(cache_key)
    if cached is not None:
        return cached

    if not search_service.search_engine.is_fitted:
        offset = (page - 1) * limit
        total = part_repo.count_search_results(q)
        results = part_repo.search_by_sql_like(q, offset=offset, limit=limit)
        paginated = results
        response_data = {
            "results": paginated,
            "count": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit,
            "fallback": True
        }
        search_cache.set(cache_key, response_data)
        return response_data

    top_k_needed = limit * page + limit
    all_results = search_service.search_parts(q, category=None, top_k=top_k_needed)
    total = len(all_results)
    start = (page - 1) * limit
    end = start + limit
    paginated = all_results[start:end]
    response_data = {
        "results": paginated,
        "count": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }
    search_cache.set(cache_key, response_data)
    return response_data
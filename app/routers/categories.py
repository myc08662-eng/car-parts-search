from fastapi import APIRouter
from app.repositories import category_repo
from app.models import CategoryResponse

router = APIRouter(prefix="/api/categories", tags=["categories"])

@router.get("", response_model=list[CategoryResponse])
async def get_categories():
    return category_repo.get_all_categories()
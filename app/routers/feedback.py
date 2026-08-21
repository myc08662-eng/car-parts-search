from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import get_db_connection

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

class FeedbackData(BaseModel):
    query: str
    category: str = ""
    page: int = 1
    page_limit: int = 20
    rating: int  # 1 = полезно, 0 = бесполезно
    results_count: int = 0

@router.post("")
async def save_feedback(data: FeedbackData):
    if data.rating not in (0, 1):
        raise HTTPException(status_code=400, detail="rating must be 0 or 1")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO search_feedback (query, category, page, page_limit, rating, results_count)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (data.query, data.category, data.page, data.page_limit, data.rating, data.results_count)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "ok"}
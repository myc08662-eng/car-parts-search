from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from app.templating import templates
from app.repositories import instruction_repo
from app.database import get_db_connection
import os

router = APIRouter(tags=["instructions"])

@router.get("/instructions/{car_id}", response_class=HTMLResponse)
async def show_instructions(request: Request, car_id: int):
    car = instruction_repo.get_car_by_id(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Автомобиль не найден")
    
    instructions = instruction_repo.get_instructions_by_car(car_id)
    car_name = f"{car['brand']} {car['model']} {car['generation'] or ''}".strip()
    
    return templates.TemplateResponse("instructions.html", {
        "request": request,
        "car_name": car_name,
        "instructions": instructions
    })

@router.get("/api/instructions/download/{instruction_id}")
async def download_instruction(instruction_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT file_path, title FROM instructions WHERE id = %s",
        (instruction_id,)
    )
    instruction = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not instruction or not instruction['file_path']:
        raise HTTPException(status_code=404, detail="Инструкция не найдена или файл отсутствует")
    
    file_path = instruction['file_path']
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # корень проекта
    if file_path.startswith('/static/'):
        full_path = os.path.join(base_dir, file_path.lstrip('/'))
    else:
        full_path = file_path  
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    return FileResponse(
        path=full_path,
        filename=os.path.basename(full_path),
        media_type='application/pdf'
    )
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from app.repositories import instruction_repo
from app.templating import templates

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
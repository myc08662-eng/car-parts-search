from pydantic import BaseModel
from typing import Optional

class PartLinkResponse(BaseModel):
    part_id: int
    car_id: int
    part_name: str
    car_name: str
    category: Optional[str] = None
    price: Optional[float] = None
    url: str
    vendor: Optional[str] = None
    similarity: Optional[float] = None

class InstructionResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    file_path: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
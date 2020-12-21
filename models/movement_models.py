from pydantic import BaseModel
from datetime import datetime

class MovementIn(BaseModel):
    username: str
    password: str
    concept: str
    amount: float

class MovementOut(BaseModel):
    id_movement: int
    username: str
    date: datetime
    concept: str
    amount: float
    budget: float
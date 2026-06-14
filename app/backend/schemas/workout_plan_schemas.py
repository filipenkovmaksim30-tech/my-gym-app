from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class CreateWorkoutPlan(BaseModel):
    date: date
    title: str = Field(..., max_length=30)

class EditWorkoutPlan(BaseModel):
    date: Optional[date] = None
    title: Optional[str] = Field(None, max_length=30)


class WorkoutPlanResponse(BaseModel):
    id: int
    user_id: int
    date: date
    title: str

    class Config:
        from_attributes = True

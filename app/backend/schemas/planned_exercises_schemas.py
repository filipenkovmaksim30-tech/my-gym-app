from pydantic import BaseModel, Field
from typing import List, Optional

from app.backend.schemas.planned_set_schemas import PlannedSetResponse
from app.backend.schemas.actual_set_schemas import ActualSetResponse

class CreatePlannedExercises(BaseModel):
    workout_plan_id: int
    exercise_name: str = Field(..., max_length=30)

class EditPlannedExercises(BaseModel):
    exercise_name: Optional[str] = Field(None, max_length=30)

class PlannedExercisesResponse(BaseModel):
    id: int
    workout_plan_id: int
    exercise_name: str
    
    planned_sets: List[PlannedSetResponse] = []
    actual_sets: List[ActualSetResponse] = []

    class Config:
        from_attributes = True
from pydantic import BaseModel, Field
from typing import Optional

class PlannedSetBase(BaseModel):
    set_number: int = Field(..., ge=1)
    target_weight: Optional[float] = Field(None, ge=0)
    target_reps: int = Field(..., ge=1)

class CreatePlannedSet(PlannedSetBase):
    planned_exercise_id: int

class EditPlannedSet(BaseModel):
    set_number: Optional[int] = Field(None, ge=1)
    target_weight: Optional[float] = Field(None, ge=0)
    target_reps: Optional[int] = Field(None, ge=1)

class PlannedSetResponse(PlannedSetBase):
    id: int
    planned_exercise_id: int

    class Config:
        from_attributes = True
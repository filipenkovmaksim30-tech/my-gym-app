from pydantic import BaseModel, Field
from typing import Optional

class ActualSetBase(BaseModel):
    set_number: int = Field(..., ge=1)
    weight: float = Field(..., ge=0)
    reps_done: int = Field(..., ge=0)

class CreateActualSet(ActualSetBase):
    planned_exercise_id: int

class EditActualSet(BaseModel):
    set_number: Optional[int] = Field(None, ge=1)
    weight: Optional[float] = Field(None, ge=0)
    reps_done: Optional[int] = Field(None, ge=0)

class ActualSetResponse(ActualSetBase):
    id: int
    planned_exercise_id: int

    class Config:
        from_attributes = True
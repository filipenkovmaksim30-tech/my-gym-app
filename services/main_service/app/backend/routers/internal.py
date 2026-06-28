from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.databases.database import get_session
from app.backend.crud.internal import get_user_workout_progress

router = APIRouter(prefix="/api/internal", tags=["Internal"])

@router.get("/workout-history/{user_id}")
async def get_workout_history(user_id: int, session: AsyncSession = Depends(get_session)):
    real_data = await get_user_workout_progress(session, user_id=user_id)
    
    return real_data
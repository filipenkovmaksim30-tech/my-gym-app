from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.databases.models import WorkoutPlan 

async def get_user_workout_progress(session: AsyncSession, user_id: int):
    query = (
        select(WorkoutPlan.date, WorkoutPlan.weight)
        .where(WorkoutPlan.user_id == user_id)
        .order_by(WorkoutPlan.date.asc())
    )
    
    result = await session.execute(query)
    rows = result.all()

    if not rows:
        return {"dates": [], "weights": []}

    dates = [row.date.strftime("%d.%m") for row in rows]
    weights = [float(row.weight) for row in rows]

    return {
        "dates": dates,
        "weights": weights
    }
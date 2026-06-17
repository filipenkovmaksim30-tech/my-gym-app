from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.backend.databases.models import PlannedSet, PlannedExercise, WorkoutPlan
from app.backend.schemas.planned_set_schemas import CreatePlannedSet, EditPlannedSet

async def init_planned_set(session: AsyncSession, planned_set_data: CreatePlannedSet, user_id: int):
    query = (
        select(PlannedExercise)
        .join(WorkoutPlan)
        .where(PlannedExercise.id == planned_set_data.planned_exercise_id, WorkoutPlan.user_id == user_id)
    )
    result = await session.execute(query)
    if not result.scalar_one_or_none():
        return None

    new_set = PlannedSet(**planned_set_data.model_dump())
    session.add(new_set)
    await session.commit()
    await session.refresh(new_set)
    return new_set

async def edit_planned_set(session: AsyncSession, update_data: EditPlannedSet, set_id: int, user_id: int):
    query = (
        select(PlannedSet)
        .join(PlannedExercise)
        .join(WorkoutPlan)
        .where(PlannedSet.id == set_id, WorkoutPlan.user_id == user_id)
    )
    result = await session.execute(query)
    db_set = result.scalar_one_or_none()
    
    if not db_set:
        return False
        
    updated_fields = update_data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updated_fields.items():
        setattr(db_set, key, value)
        
    await session.commit()
    await session.refresh(db_set)
    return db_set

async def delete_planned_set(session: AsyncSession, set_id: int, user_id: int):
    query = (
        select(PlannedSet)
        .join(PlannedExercise)
        .join(WorkoutPlan)
        .where(PlannedSet.id == set_id, WorkoutPlan.user_id == user_id)
    )
    result = await session.execute(query)
    db_set = result.scalar_one_or_none()
    
    if not db_set:
        return False
        
    await session.delete(db_set)
    await session.commit()
    return True
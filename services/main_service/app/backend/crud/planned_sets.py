from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.backend.databases.models import PlannedSet, PlannedExercise, WorkoutPlan
from app.backend.schemas.planned_set_schemas import CreatePlannedSet, EditPlannedSet

async def init_planned_set(session: AsyncSession, planned_set_data: CreatePlannedSet, user_id: int):
    query = (
        select(PlannedExercise)
        .join(WorkoutPlan)
        .where(PlannedExercise.id == planned_set_data.planned_exercise_id, WorkoutPlan.user_id == user_id)
    )
    result = await session.execute(query)
    exercise = result.scalar_one_or_none()
    
    if not exercise:
        return None
    
    new_set = PlannedSet(**planned_set_data.model_dump())
    session.add(new_set)
    await session.commit()

    stmt = (
        select(PlannedSet)
        .options(selectinload(PlannedSet.planned_exercise))
        .where(PlannedSet.id == new_set.id)
    )
    res = await session.execute(stmt)
    return res.scalar_one()


async def edit_planned_set(session: AsyncSession, update_data: EditPlannedSet, set_id: int, user_id: int):
    query = (
        select(PlannedSet)
        .join(PlannedExercise)
        .join(WorkoutPlan)
        .options(selectinload(PlannedSet.planned_exercise))
        .where(PlannedSet.id == set_id, WorkoutPlan.user_id == user_id)
    )
    result = await session.execute(query)
    db_set = result.scalar_one_or_none()
    
    if not db_set:
        return None
        
    updated_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updated_dict.items():
        setattr(db_set, key, value)
        
    await session.commit()
    
    stmt = (
        select(PlannedSet)
        .options(selectinload(PlannedSet.planned_exercise))
        .where(PlannedSet.id == db_set.id)
    )
    res = await session.execute(stmt)
    return res.scalar_one()


async def delete_planned_set(session: AsyncSession, set_id: int, user_id: int):
    query = (
        select(PlannedSet)
        .join(PlannedExercise)
        .join(WorkoutPlan)
        .options(selectinload(PlannedSet.planned_exercise))
        .where(PlannedSet.id == set_id, WorkoutPlan.user_id == user_id)
    )
    result = await session.execute(query)
    db_set = result.scalar_one_or_none()
    
    if not db_set:
        return None
        
    await session.delete(db_set)
    await session.commit()
    
    return db_set
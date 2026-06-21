from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.databases.models import ActualSet, WorkoutPlan, PlannedExercise
from backend.schemas.actual_set_schemas import CreateActualSet, EditActualSet

async def init_actual_set(session: AsyncSession, actual_data: CreateActualSet, user_id: int):
    query = (
        select(PlannedExercise)
        .join(WorkoutPlan)
        .where(PlannedExercise.id == actual_data.planned_exercise_id, WorkoutPlan.user_id == user_id)
    )
    result = await session.execute(query)
    exercise = result.scalar_one_or_none()
    
    if not exercise:
        return None
    
    new_actual_set = ActualSet(**actual_data.model_dump())
    session.add(new_actual_set)
    await session.commit()
    
    stmt = (
        select(ActualSet)
        .options(selectinload(ActualSet.planned_exercise))
        .where(ActualSet.id == new_actual_set.id)
    )
    res = await session.execute(stmt)
    return res.scalar_one()

async def edit_actual_set(session: AsyncSession, actual_set_id: int, updated_data: EditActualSet, user_id: int):
    query = (
        select(ActualSet)
        .join(PlannedExercise)
        .join(WorkoutPlan)
        .options(selectinload(ActualSet.planned_exercise))
        .where(ActualSet.id == actual_set_id, WorkoutPlan.user_id == user_id)
    )

    result = await session.execute(query)
    db_actual_set = result.scalar_one_or_none()

    if not db_actual_set:
        return None
    
    updated_dict = updated_data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updated_dict.items():
        setattr(db_actual_set, key, value)

    await session.commit()
    

    stmt = (
        select(ActualSet)
        .options(selectinload(ActualSet.planned_exercise))
        .where(ActualSet.id == db_actual_set.id)
    )
    res = await session.execute(stmt)
    return res.scalar_one()

async def delete_actual_set_by_id(session: AsyncSession, actual_set_id: int, user_id: int):
    query = (
        select(ActualSet)
        .join(PlannedExercise)
        .join(WorkoutPlan)
        .options(selectinload(ActualSet.planned_exercise))
        .where(ActualSet.id == actual_set_id, WorkoutPlan.user_id == user_id)
    )

    result = await session.execute(query)
    db_actual_set = result.scalar_one_or_none()

    if not db_actual_set:
        return None
    
    await session.delete(db_actual_set)
    await session.commit()
    
    return db_actual_set
    
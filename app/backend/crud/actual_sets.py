from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.backend.databases.models import ActualSet, WorkoutPlan, PlannedExercise
from app.backend.schemas.actual_set_schemas import ActualSetBase, ActualSetResponse, CreateActualSet, EditActualSet

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
    await session.refresh(new_actual_set)
    return new_actual_set

async def edit_actual_set(session: AsyncSession, actual_set_id: int, updated_data: EditActualSet, user_id: int):
    query = (
        select(ActualSet)
        .join(PlannedExercise)
        .join(WorkoutPlan)
        .where(ActualSet.id == actual_set_id, WorkoutPlan.user_id == user_id)
    )

    result = await session.execute(query)
    db_actual_set = result.scalar_one_or_none()

    if not db_actual_set:
        return False
    
    updated_dict = updated_data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updated_dict.items():
        setattr(db_actual_set, key, value)

    await session.commit()
    await session.refresh(db_actual_set)
    return db_actual_set

async def delete_actual_set_by_id(session: AsyncSession, actual_set_id: int, user_id: int):
    query = (
        select(ActualSet)
        .join(PlannedExercise)
        .join(WorkoutPlan)
        .where(ActualSet.id == actual_set_id, WorkoutPlan.user_id == user_id)
    )

    result = await session.execute(query)
    db_actual_set = result.scalar_one_or_none()

    if not db_actual_set:
        return False
    
    await session.delete(db_actual_set)
    await session.commit()
    return {
        "success": True,
        "message": "Актуальный подход удален"
    }
    
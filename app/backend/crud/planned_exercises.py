from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.databases.models import PlannedExercise, WorkoutPlan
from backend.schemas.planned_exercises_schemas import CreatePlannedExercises, EditPlannedExercises

async def init_planned_exercises(session: AsyncSession, planned_exercises: CreatePlannedExercises):
    planned_exercises_data = planned_exercises.model_dump()
    new_planned_exercise = PlannedExercise(**planned_exercises_data)

    session.add(new_planned_exercise)
    await session.commit()
    await session.refresh(
        new_planned_exercise, 
        attribute_names=["planned_sets", "actual_sets"]
    )
    return new_planned_exercise


async def get_planned_exercises_by_id(session: AsyncSession, planned_exercises_id: int, user_id: int):
    query = (
        select(PlannedExercise)
        .join(WorkoutPlan)
        .where(PlannedExercise.id == planned_exercises_id, WorkoutPlan.user_id == user_id)
        .options(
            selectinload(PlannedExercise.planned_sets),
            selectinload(PlannedExercise.actual_sets)
        )
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_all_planned_exercises_by_workout_plan_id(session: AsyncSession, workout_plan_id: int, user_id: int):
    plan_check = await session.execute(
        select(WorkoutPlan).where(WorkoutPlan.id == workout_plan_id, WorkoutPlan.user_id == user_id)
    )
    if not plan_check.scalar_one_or_none():
        return None

    query = (
        select(PlannedExercise)
        .where(PlannedExercise.workout_plan_id == workout_plan_id)
        .options(
            selectinload(PlannedExercise.planned_sets),
            selectinload(PlannedExercise.actual_sets)
        )
    )
    result = await session.execute(query)
    return result.scalars().all()

async def edit_planned_exercises(session: AsyncSession, update_data: EditPlannedExercises, planned_exercise_id: int, user_id: int):
    query = (
        select(PlannedExercise)
        .join(WorkoutPlan)
        .where(PlannedExercise.id == planned_exercise_id, WorkoutPlan.user_id == user_id)
        .options(
            selectinload(PlannedExercise.planned_sets),
            selectinload(PlannedExercise.actual_sets)
        )
    )
    result = await session.execute(query)
    db_exercises = result.scalar_one_or_none()
    if not db_exercises:
        return False
    
    updated_fields = update_data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updated_fields.items():
        setattr(db_exercises, key, value)
    
    await session.commit()
    await session.refresh(db_exercises)
    return db_exercises


async def delete_planned_exercises(session: AsyncSession, planned_exercises_id: int, user_id: int):
    query = (
        select(PlannedExercise)
        .join(WorkoutPlan)
        .where(PlannedExercise.id == planned_exercises_id, WorkoutPlan.user_id == user_id)
    )
    result = await session.execute(query)
    db_exercise = result.scalar_one_or_none()
    
    if not db_exercise:
        return False
        
    await session.delete(db_exercise)
    await session.commit()
    
    return {
        "success": True,
        "message": "Запланированное упражнение успешно удалено"
    }
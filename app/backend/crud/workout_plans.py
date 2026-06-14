from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.databases.models import WorkoutPlan
from app.backend.schemas.workout_plan_schemas import CreateWorkoutPlan, WorkoutPlanResponse, EditWorkoutPlan


async def init_workplan(session: AsyncSession, workoutplan: CreateWorkoutPlan, user_id: int):
    plan_data = workoutplan.model_dump()
    plan_data["user_id"] = user_id

    new_workoutplan = WorkoutPlan(**plan_data)

    session.add(new_workoutplan)
    await session.commit()
    await session.refresh(new_workoutplan)
    return new_workoutplan

async def get_workplan_by_id(session: AsyncSession, workplan_id: int, user_id: int):
    query = await session.execute(
        select(WorkoutPlan).where(WorkoutPlan.id == workplan_id, WorkoutPlan.user_id == user_id)
    )
    workoutplan_data = query.scalar_one_or_none()
    return workoutplan_data

async def get_all_workplans_by_user(session: AsyncSession, user_id: int):
    query = await session.execute(
        select(WorkoutPlan).where(WorkoutPlan.user_id == user_id)
    )
    return query.scalars().all()

async def update_workplan_by_id(session: AsyncSession, workplan_id: int, user_id: int, workoutplan: EditWorkoutPlan):
    query = await session.execute(
        select(WorkoutPlan).where(WorkoutPlan.id == workplan_id, WorkoutPlan.user_id == user_id)
    )
    workplan_data = query.scalar_one_or_none()
    
    if not workplan_data:
        return None
    
    update_data = workoutplan.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in update_data.items():
        setattr(workplan_data, key, value)

    await session.commit()
    await session.refresh(workplan_data)
    return workplan_data

async def delete_workplan_by_id(session: AsyncSession, workplan_id: int, user_id: int):
    query = delete(WorkoutPlan).where(WorkoutPlan.id == workplan_id, WorkoutPlan.user_id == user_id)
    result = await session.execute(query)
    await session.commit()

    if result.rowcount == 0:
        return False
    
    return {
        "success": True,
        "message": "Тренировка успешно удалена"
    }
from fastapi import APIRouter, Depends, status, HTTPException
from typing import List

from app.backend.crud.workout_plans import init_workplan, get_workplan_by_id, update_workplan_by_id , \
delete_workplan_by_id, get_all_workplans_by_user, copy_workout_plan_to_date
from app.backend.databases.database import get_session
from app.backend.schemas.workout_plan_schemas import CreateWorkoutPlan, WorkoutPlanResponse, EditWorkoutPlan, CopyWorkoutPlanRequest
from app.backend.schemas.user_schemas import UserResponse
from app.backend.auth.auth import get_current_user

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Workoutplan"], prefix="/workoutplan")


@router.post("",
    response_model=WorkoutPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание плана дня тренировки"    
)
async def create_workoutplan(
    workoutplan_data: CreateWorkoutPlan,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    new_workplan = await init_workplan(session, workoutplan_data, current_user.id)

    return new_workplan

@router.get("/{workoutplan_id}",
    status_code=status.HTTP_200_OK,
    summary="Получить план тренировки по ID"        
)
async def read_workoutplan(
    workoutplan_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    result = await get_workplan_by_id(session, workoutplan_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="План тренировки не найден")
    return result

@router.get("",
    response_model=List[WorkoutPlanResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить все планы тренировок текущего пользователя"    
)
async def read_all_read_workoutplans(
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    workoutplans = await get_all_workplans_by_user(session, current_user.id)
    return workoutplans

@router.post("/{workout_plan_id}/copy",
    response_model=WorkoutPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Скопировать тренировку (без подходов)"
)
async def copy_workout_plan(
    workout_plan_id: int,
    payload: CopyWorkoutPlanRequest,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    copyied_plan = await copy_workout_plan_to_date(session, workout_plan_id, payload.new_data, current_user.id)

    if not copyied_plan:
        raise HTTPException(status_code=404, detail="Тренировка для копирования не найдена или доступ запрещен")
    
    return copyied_plan

@router.patch("/{workoutplan_id}",
    status_code=status.HTTP_200_OK,
    summary="Редактирование плана тренировки по ID"    
)
async def edit_workoutplan(
    workoutplan_id: int,
    workplan_data: EditWorkoutPlan,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    updated_plan = await update_workplan_by_id(session, workoutplan_id, current_user.id, workplan_data)
    if not updated_plan:
        raise HTTPException(status_code=404, detail="План тренировки не найден или нет прав")
    return updated_plan

@router.delete("/{workoutplan_id}",
    status_code=status.HTTP_200_OK,
    summary="Удаление плана тренировки по ID"        
)
async def delete_workoutplan(
    workoutplan_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    deleted = await delete_workplan_by_id(session, workoutplan_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"План с ID {workoutplan_id} не найден")
    return {"success": True, "message": "План тренировки удален"}
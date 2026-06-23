from fastapi import APIRouter, Depends, status, HTTPException
from typing import List

from services.main_service.app.backend.crud.workout_plans import init_workplan, get_workplan_by_id, update_workplan_by_id , \
delete_workplan_by_id, get_all_workplans_by_user, copy_workout_plan_to_date
from services.main_service.app.backend.databases.database import get_session
from services.main_service.app.backend.schemas.workout_plan_schemas import CreateWorkoutPlan, WorkoutPlanResponse, EditWorkoutPlan, CopyWorkoutPlanRequest
from services.main_service.app.backend.schemas.user_schemas import UserResponse
from services.main_service.app.backend.auth.auth import get_current_user

from sqlalchemy.ext.asyncio import AsyncSession
from services.main_service.app.backend.cache.redis import cache_backend


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
    await cache_backend.delete_cache(f"user_plan:{current_user.id}")
    return WorkoutPlanResponse.model_validate(new_workplan).model_dump()


@router.get("/{workoutplan_id}",
    response_model=WorkoutPlanResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить план тренировки по ID"        
)
async def read_workoutplan(
    workoutplan_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    cache_key = f"workoutplan:{workoutplan_id}"

    cached_data = await cache_backend.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    plan_data = await get_workplan_by_id(session, workoutplan_id, current_user.id)
    if not plan_data:
        raise HTTPException(status_code=404, detail="План тренировки не найден")
    
    json_response = WorkoutPlanResponse.model_validate(plan_data).model_dump()
    await cache_backend.set_cache(cache_key, json_response)
    
    return json_response


@router.get("",
    response_model=List[WorkoutPlanResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить все планы тренировок текущего пользователя"    
)
async def read_all_workoutplans(
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    cache_key = f"user_plan:{current_user.id}"

    cached_data = await cache_backend.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    workoutplans = await get_all_workplans_by_user(session, current_user.id)
    
    json_response = [WorkoutPlanResponse.model_validate(plan).model_dump() for plan in workoutplans]
    await cache_backend.set_cache(cache_key, json_response)

    return json_response


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
    
    await cache_backend.delete_cache(f"user_plan:{current_user.id}")
    return WorkoutPlanResponse.model_validate(copyied_plan).model_dump()


@router.patch("/{workoutplan_id}",
    response_model=WorkoutPlanResponse,
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
    
    await cache_backend.delete_cache(f"workoutplan:{workoutplan_id}")
    await cache_backend.delete_cache(f"user_plan:{current_user.id}")
    return WorkoutPlanResponse.model_validate(updated_plan).model_dump()


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
    
    await cache_backend.delete_cache(f"workoutplan:{workoutplan_id}")
    await cache_backend.delete_cache(f"user_plan:{current_user.id}")

    await cache_backend.delete_by_pattern(f"workout_plan_exercise:{workoutplan_id}*")

    return {"success": True, "message": "План тренировки удален"}
from fastapi import APIRouter, Depends, status, HTTPException
from typing import List

from services.main_service.app.backend.crud.planned_exercises import init_planned_exercises, get_all_planned_exercises_by_workout_plan_id,\
get_planned_exercises_by_id, edit_planned_exercises, delete_planned_exercises
from services.main_service.app.backend.schemas.planned_exercises_schemas import PlannedExercisesResponse, EditPlannedExercises, CreatePlannedExercises
from services.main_service.app.backend.schemas.user_schemas import UserResponse
from services.main_service.app.backend.auth.auth import get_current_user
from services.main_service.app.backend.databases.database import get_session
from services.main_service.app.backend.cache.redis import cache_backend
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["PlannedExercises"], prefix="/planned_exercises")

@router.post("",
    response_model=PlannedExercisesResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать запланированное упражнение"    
)
async def create_planned_exercises(
    planned_exercise: CreatePlannedExercises,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    new_planned_exercises = await init_planned_exercises(session, planned_exercise)

    await cache_backend.delete_cache(f"workout_plan_exercise:{planned_exercise.workout_plan_id}")
    await cache_backend.delete_cache(f"user_plan:{current_user.id}")

    return new_planned_exercises

@router.get("/{planned_exercise_id}", 
    response_model=PlannedExercisesResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить запланированное упражнение по ID"
)
async def read_planned_exercise(
    planned_exercise_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    cache_key = f"planned_exercise:{planned_exercise_id}"

    cached_data = await cache_backend.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    exercise_data = await get_planned_exercises_by_id(session, planned_exercise_id, current_user.id)
    if not exercise_data:
        raise HTTPException(status_code=404, detail="Упражнение не найдено")

    json_response = PlannedExercisesResponse.model_validate(exercise_data).model_dump()
    await cache_backend.set_cache(cache_key, json_response)

    return json_response

@router.get("/workout/{workout_plan_id}",
    response_model=List[PlannedExercisesResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить все запланированные упражнения по ID тренировки"
)
async def read_all_planned_exercises_by_workout_plan_id(
    workout_plan_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    cache_key = f"workout_plan_exercise:{workout_plan_id}"

    cache_data = await cache_backend.get_cache(cache_key)
    if cache_data is not None:
        return cache_data

    result = await get_all_planned_exercises_by_workout_plan_id(session, workout_plan_id, current_user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="План тренировки не найден или доступ запрещен")
        
    json_response = [PlannedExercisesResponse.model_validate(ex).model_dump() for ex in result]
    await cache_backend.set_cache(cache_key, json_response)

    return json_response

@router.put("/{planned_exercises_id}",
    response_model=PlannedExercisesResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить запланированное упражнение по ID" 
)
async def update_planned_exercise_by_id(
    planned_exercises_id: int,
    updated_data: EditPlannedExercises,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    updated = await edit_planned_exercises(session, updated_data, planned_exercises_id, current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Упражнение не найдено или нет прав")
    
    await cache_backend.delete_cache(f"planned_exercise:{planned_exercises_id}")
    await cache_backend.delete_cache(f"workout_plan_exercise:{updated.workout_plan_id}")
    await cache_backend.delete_cache(f"user_plan:{current_user.id}")

    return updated

@router.delete("/{planned_exercises_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить запланированное упражнение по ID"    
)
async def delete_planned_exercises_by_id(
    planned_exercises_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    exercise = await get_planned_exercises_by_id(session, planned_exercises_id, current_user.id)
    if not exercise:
        raise HTTPException(status_code=404, detail=f"Упражнение с ID {planned_exercises_id} не найдено")
    
    workout_plan_id = exercise.workout_plan_id

    deleted = await delete_planned_exercises(session, planned_exercises_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Упражнение с ID {planned_exercises_id} не найдено")
    
    await cache_backend.delete_cache(f"planned_exercise:{planned_exercises_id}")
    await cache_backend.delete_cache(f"workout_plan_exercise:{workout_plan_id}")
    await cache_backend.delete_cache(f"user_plan:{current_user.id}")
    
    return {"success": True, "message": "Упражнение удалено"}
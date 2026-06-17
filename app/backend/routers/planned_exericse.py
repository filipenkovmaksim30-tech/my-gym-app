from fastapi import APIRouter, Depends, status, HTTPException
from typing import List

from app.backend.crud.planned_exercises import init_planned_exercises, get_all_planned_exercises_by_workout_plan_id,\
get_planned_exercises_by_id, edit_planned_exercises, delete_planned_exercises
from app.backend.schemas.planned_exercises_schemas import PlannedExercisesResponse, EditPlannedExercises, CreatePlannedExercises
from app.backend.schemas.user_schemas import UserResponse
from app.backend.auth.auth import get_current_user
from app.backend.databases.database import get_session

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
    return new_planned_exercises

@router.get("/{planned_exercises_id}",
    response_model=PlannedExercisesResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить запланированное упражнение по ID"    
)
async def read_planned_exercise_by_id(
    planned_exercises_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    result = await get_planned_exercises_by_id(session, planned_exercises_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Упражнение не найдено")
    return result

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
    result = await get_all_planned_exercises_by_workout_plan_id(session, workout_plan_id, current_user.id)
    
    if result is None:
        raise HTTPException(status_code=404, detail="План тренировки не найден или доступ запрещен")
        
    return result

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
    deleted = await delete_planned_exercises(session, planned_exercises_id, current_user.id)

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Упражнение с ID {planned_exercises_id} не найдено")
    return {"success": True, "message": "Упражнение удалено"}
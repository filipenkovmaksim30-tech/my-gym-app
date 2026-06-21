from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.planned_sets import init_planned_set, edit_planned_set, delete_planned_set
from backend.schemas.planned_set_schemas import PlannedSetResponse, CreatePlannedSet, EditPlannedSet
from backend.schemas.user_schemas import UserResponse
from backend.auth.auth import get_current_user
from backend.databases.database import get_session

from backend.cache.redis import cache_backend

router = APIRouter(tags=["PlannedSets"], prefix="/planned_sets")

@router.post("",
    response_model=PlannedSetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить запланированный подход к упражнению"
)
async def create_set(
    planned_set_data: CreatePlannedSet,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):

    new_set = await init_planned_set(session, planned_set_data, current_user.id)
    if not new_set:
        raise HTTPException(status_code=404, detail="Упражнение не найдено или доступ запрещен")
    
    exercise_id = planned_set_data.planned_exercise_id
    

    await cache_backend.delete_cache(f"planned_exercise:{exercise_id}")
    await cache_backend.delete_cache(f"workout_plan_exercise:{new_set.planned_exercise.workout_plan_id}")
    await cache_backend.delete_cache(f"user_plan:{current_user.id}")

    return new_set

@router.put("/{set_id}",
    response_model=PlannedSetResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить запланированный подход по ID"
)
async def update_set(
    set_id: int,
    update_data: EditPlannedSet,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):

    updated = await edit_planned_set(session, update_data, set_id, current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Подход не найден или доступ запрещен")
    
    await cache_backend.delete_cache(f"planned_exercise:{updated.planned_exercise_id}")
    await cache_backend.delete_cache(f"workout_plan_exercise:{updated.planned_exercise.workout_plan_id}")
    await cache_backend.delete_cache(f"user_plan:{current_user.id}")

    return updated

@router.delete("/{set_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить запланированный подход по ID"
)
async def delete_set(
    set_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    deleted_set = await delete_planned_set(session, set_id, current_user.id)
    if not deleted_set:
        raise HTTPException(status_code=404, detail="Подход не найден или доступ запрещен")
    
    await cache_backend.delete_cache(f"planned_exercise:{deleted_set.planned_exercise_id}")
    await cache_backend.delete_cache(f"workout_plan_exercise:{deleted_set.planned_exercise.workout_plan_id}")
    await cache_backend.delete_cache(f"user_plan:{current_user.id}")

    return {"success": True, "message": "Запланированный подход успешно удален"}
from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from backend.databases.database import get_session
from backend.auth.auth import get_current_user
from backend.crud.actual_sets import init_actual_set, edit_actual_set, delete_actual_set_by_id
from backend.schemas.actual_set_schemas import ActualSetResponse, EditActualSet, CreateActualSet
from backend.schemas.user_schemas import UserResponse

from backend.cache.redis import cache_backend

router = APIRouter(tags=["ActualSet"], prefix="/actual_sets")

@router.post("",
    response_model=ActualSetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать актуальный подход"   
)
async def create_actual_set(
    actual_set_data: CreateActualSet,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    new_set = await init_actual_set(session, actual_set_data, current_user.id)

    if not new_set:
        raise HTTPException(status_code=404, detail="Не удалось создать актуальный подход")
    
    exercise_id = actual_set_data.planned_exercise_id

    await cache_backend.delete_cache(f"planned_exercise:{exercise_id}")
    await cache_backend.delete_cache(f"workout_plan_exercise:{new_set.planned_exercise.workout_plan_id}")
    await cache_backend.delete_cache(f"user_plan:{current_user.id}")

    return new_set

@router.put("/{actual_set_id}",
    response_model=ActualSetResponse,
    status_code=status.HTTP_200_OK,
    summary="Изменить актуальный подход"
)
async def update_actual_set(
    actual_set_id: int,
    update_data: EditActualSet,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    updated = await edit_actual_set(session,  actual_set_id, update_data, current_user.id)

    if not updated:
        raise HTTPException(status_code=404, detail="Актуальный подход не найден или доступ запрещен")
    
    await cache_backend.delete_cache(f"planned_exercise:{updated.planned_exercise_id}")
    await cache_backend.delete_cache(f"workout_plan_exercise:{updated.planned_exercise.workout_plan_id}")
    await cache_backend.delete_cache(f"user_plan:{current_user.id}")    

    return updated

@router.delete("/{actual_set_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить актуальный подход"
)
async def delete_actual_set(
    actual_set_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    deleted_set = await delete_actual_set_by_id(session, actual_set_id, current_user.id)

    if not deleted_set:
        raise HTTPException(status_code=404, detail="Актуальный подход не найден или доступ запрещен")
    
    await cache_backend.delete_cache(f"planned_exercise:{deleted_set.planned_exercise_id}")
    await cache_backend.delete_cache(f"workout_plan_exercise:{deleted_set.planned_exercise.workout_plan_id}")
    await cache_backend.delete_cache(f"user_plan:{current_user.id}") 

    return {"success": True, "message": "Актуальный подход успешно удален"}
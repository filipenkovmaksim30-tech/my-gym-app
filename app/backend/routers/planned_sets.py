from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.crud.planned_sets import init_planned_set, edit_planned_set, delete_planned_set
from app.backend.schemas.planned_set_schemas import PlannedSetResponse, CreatePlannedSet, EditPlannedSet
from app.backend.schemas.user_schemas import UserResponse
from app.backend.auth.auth import get_current_user
from app.backend.databases.database import get_session

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
    deleted = await delete_planned_set(session, set_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Подход не найден или доступ запрещен")
    return {"success": True, "message": "Запланированный подход успешно удален"}
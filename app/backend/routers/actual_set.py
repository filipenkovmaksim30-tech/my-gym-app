from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.databases.database import get_session
from app.backend.auth.auth import get_current_user
from app.backend.crud.actual_sets import init_actual_set, edit_actual_set, delete_actual_set_by_id
from app.backend.schemas.actual_set_schemas import ActualSetResponse, EditActualSet, CreateActualSet
from app.backend.schemas.user_schemas import UserResponse

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
    deleted = await delete_actual_set_by_id(session, actual_set_id, current_user.id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Актуальный подход не найден или доступ запрещен")
    
    return {"success": True, "message": "Актуальный подход успешно удален"}
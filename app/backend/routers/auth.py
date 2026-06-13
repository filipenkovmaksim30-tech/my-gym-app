from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.backend.databases.database import get_session
from app.backend.crud.users import create_user, get_user_by_username
from app.backend.schemas.user_schemas import UserCreate, UserResponse
from app.backend.databases.models import User
from app.backend.auth.auth import create_access_token
from app.backend.auth.security import verify_password

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=['Authorization'], prefix='/auth')

@router.post("/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя"
)
async def register(
    user_data: UserCreate, 
    session: AsyncSession = Depends(get_session)
):
    existing_user = await get_user_by_username(session, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )

    new_user = await create_user(session, user_data)

    return new_user

@router.post("/login",
   status_code=status.HTTP_200_OK,
   summary="Вход в систему (Установка Cookies)"          
)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    user = await get_user_by_username(session, form_data.username)

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = create_access_token(data={"sub": str(user.id)})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False, # поставить True при деплое 
        samesite="lax",
        max_age=1800
    )
    return {
        "success": True,
        "message" : "Вы успешно вошли в систему"
    }


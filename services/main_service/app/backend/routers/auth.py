from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm

from services.main_service.app.backend.databases.database import get_session
from services.main_service.app.backend.crud.users import create_user, get_user_by_username, change_user_password
from services.main_service.app.backend.schemas.user_schemas import UserCreate, UserResponse, ChangePassword
from services.main_service.app.backend.databases.models import User
from services.main_service.app.backend.auth.auth import create_access_token, get_current_user
from services.main_service.app.backend.auth.security import verify_password

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


@router.post("/change-password",
     status_code=status.HTTP_200_OK,
     summary="Смена пароля пользователя"   
)
async def change_password(
    password_data: ChangePassword,
    session: AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    result = await change_user_password(
        session,
        user_id=current_user.id,
        password_data=password_data
    )
    return result



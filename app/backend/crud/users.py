from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.schemas.user_schemas import UserCreate, UserLogin, ChangePassword
from app.backend.databases.models import User
from app.backend.auth.security import get_password_hash, verify_password
from sqlalchemy import select



async def create_user(session: AsyncSession, user: UserCreate):
    user_data = user.model_dump()
    user_data["password"] = get_password_hash(user_data["password"])

    new_user = User(**user_data)

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


async def authenticate_user(session: AsyncSession, user: UserLogin):
    query = (select(User).where(User.username == user.username))
    result = await session.execute(query)

    db_user = result.scalar_one_or_none()
    if not db_user:
        return False
    
    if not verify_password(user.password, db_user.password):
        return False
    
    return db_user




async def change_user_password(session: AsyncSession, user_id: int, password: ChangePassword):
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise ValueError("Пользователь не найден")
    
    if not verify_password(password.old_password, db_user.password_hash):
        raise ValueError("Неверный текущий пароль")
    db_user.password_hash = password.new_password

    db_user.password = get_password_hash(password.new_password)

    await session.commit()
    return {
        "success": True,
        "message": "Пароль успешно изменен",
        "user_id": db_user.id
    }
    


async def get_user_by_id(
    session: AsyncSession,
    user_id: int,
    ):
    query = await session.execute(
        select(User).where(User.id == user_id)
    )
    return query.scalar_one_or_none()

async def get_user_by_username(session: AsyncSession, username: str):
    query = select(User).where(User.username == username)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    return user
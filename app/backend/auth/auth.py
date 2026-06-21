from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
import jwt
from jwt.exceptions import PyJWTError as JWTError
from passlib.context import CryptContext

from backend.auth.config import settings
from backend.databases.database import get_session
from backend.crud.users import get_user_by_id
from backend.databases.models import User

from sqlalchemy.ext.asyncio import AsyncSession

class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(self, tokenUrl:str):
        flows = OAuthFlowsModel(password={'tokenUrl': tokenUrl, "scopes": {}})
        super().__init__(flows=flows)

    async def __call__(self, request: Request):
        token = request.cookies.get("access_token")

        if not token:
            authorization: str = request.headers.get("Autorization")
            if authorization and authorization.startswith("Bearer"):
                token = authorization.split(" ")[1]
        return token

oauth2_schema = OAuth2PasswordBearerWithCookie(tokenUrl="/auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_schema),
    session: AsyncSession = Depends(get_session)
) -> User:
    credential_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credential_exceptions
            
    except JWTError:
        raise credential_exceptions

    
    user = await get_user_by_id(session, int(user_id))
        
    if user is None:
        raise credential_exceptions

    return user


from pydantic import BaseModel, Field, EmailStr, validator, field_validator
from datetime import datetime
import re


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8, max_length=30)

    @validator("password")
    def password_requir(cls, v, values):
        if not re.search(r'\d', v):
            raise ValueError("Пароль должен содеражать хотя бы одну цифру")
        if not re.search(r'[A-Z]', v):
            raise ValueError("Пароль должен содержать заглавные буквы")
        if not re.search(r'[a-z]', v):
            raise ValueError("Пароль должен содержать строчные буквы ")
        return v 



class UserResponse(BaseModel):
    id: int
    username: str
    

class UserLogin(BaseModel):
    username: str
    password: str


class ChangePassword(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=30, description="Новый пароль")
    old_password: str = Field(..., min_length=8, max_length=30, description="Старый пароль")
    @field_validator("new_password")
    @classmethod
    def check_change_password(cls, v: str, info):
        if not re.search(r'\d', v):
            raise ValueError("Пароль должен содеражать хотя бы одну цифру")
        if not re.search(r'[A-Z]', v):
            raise ValueError("Пароль должен содержать заглавные буквы")
        if not re.search(r'[a-z]', v):
            raise ValueError("Пароль должен содержать строчные буквы ")
        if info.data.get('old_password') and v == info.data['old_password']:
            raise ValueError("Новый пароль должен отличаться от старого")
        return v
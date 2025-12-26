from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from database.setup import SessionDep
from fastapi import APIRouter, Depends, HTTPException, status

from models.user_model import UserModel
from schemas.telegram_schema import TelegramTokenAddSchema
from schemas.user_schema import UserAddSchema, Token
from api.auth.register import register, login, get_user_by_username, create_telegram_token, get_telegram_token, get_current_user, get_user_by_email

router = APIRouter(tags=["Authentification"])

@router.post("/register")
async def register_user(session: SessionDep, user: UserAddSchema):
    await register(session, user)
    return {"DB URL:": f"{session.get_bind().url}"}
    return {"User created successfully": True}

@router.post("/login")
async def login_user(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    return await login(session, form_data)

@router.post("/token")
async def insert_token(session: SessionDep, data: TelegramTokenAddSchema):
    await create_telegram_token(session, data)

@router.get("/token/{telegram_id}")
async def get_token(session: SessionDep, telegram_id: int):
    return await get_telegram_token(session, telegram_id)

@router.get("/auth/validate")
async def token_check(user: Annotated[UserModel, Depends(get_current_user)]):
    return {"detail": "OK"}

@router.get("/user/{username}")
async def get_user(session: SessionDep, username: str):
    return await get_user_by_username(session, username)

@router.get("/userm/{email}")
async def get_user_email(session: SessionDep, email: EmailStr):
    return await get_user_by_email(session, email)
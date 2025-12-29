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

@router.get("/user/register/{username}")
async def get_user_for_register(session: SessionDep, username: str):
    if await get_user_by_username(session, username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this name already exists"
        )

@router.get("/user/login/{username}")
async def get_user_for_login(session: SessionDep, username: str):
    user = await get_user_by_username(session, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

@router.get("/userm/{email}")
async def get_user_email(session: SessionDep, email: EmailStr):
    if await get_user_by_email(session, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm

from database.setup import SessionDep
from fastapi import APIRouter, Depends
from schemas.user_schema import UserAddSchema, Token
from api.auth.register import register, login, get_user_by_username
router = APIRouter(tags=["Authentification"])

@router.post("/register")
async def register_user(session: SessionDep, user: UserAddSchema):
    await register(session, user)
    return {"User created successfully": True}

@router.post("/login")
async def login_user(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    return await login(session, form_data)

@router.get("/user/{username}")
async def get_user(session: SessionDep, username: str):
    return await get_user_by_username(session, username)
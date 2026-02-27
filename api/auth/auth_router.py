from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from api.auth.functions import oauth2_scheme
from database.setup import SessionDep
from fastapi import APIRouter, Depends, HTTPException, status

from models.user_model import UserModel
from schemas.user_schema import UserAddSchema, Token
from api.auth.auth_crud import register, login, get_user_by_username, create_telegram_token, get_telegram_token, \
    get_current_user, get_user_by_email, require_role, verify_bot_secret, refresh, logout

router = APIRouter(tags=["Authentification"])

@router.post("/register")
async def register_user(session: SessionDep, user: UserAddSchema):
    await register(session, user)
    raise HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="User added successfully"
    )

@router.post("/login")
async def login_user(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    return await login(session, form_data)

@router.post("/logout")
async def logout_user(session: SessionDep, token: str = Depends(oauth2_scheme)):
    await logout(session, token)
    return {"detail": "User logged out successfully"}

@router.post("/refresh")
async def refresh_token(session: SessionDep, token: str = Depends(oauth2_scheme)):
    return await refresh(session, token)

@router.post("/token", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_bot_secret)])
async def insert_token(
        session: SessionDep,
        telegram_id: int,
        user: Annotated[UserModel, Depends(get_current_user)],
        token: str = Depends(oauth2_scheme)
):
    await create_telegram_token(session, telegram_id, user, token)
    return {"detail": "Token added successfully"}

@router.get("/token/{telegram_id}", dependencies=[Depends(verify_bot_secret)])
async def get_token(session: SessionDep, telegram_id: int):
    return await get_telegram_token(session, telegram_id)

@router.get("/auth/validate")
async def token_check(user: Annotated[UserModel, Depends(get_current_user)]):
    return {"detail": "OK"}

@router.get("/auth/validate/admin")
async def admin_check(admin=Depends(require_role)):
    return {"detail": "OK"}

@router.get("/user/register/{username}")
async def get_user_for_register(session: SessionDep, username: str):
    if await get_user_by_username(session, username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this name already exists"
        )
    return {"detail": "OK"}

@router.get("/user/login/{username}")
async def get_user_for_login(session: SessionDep, username: str):
    if await get_user_by_username(session, username) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {username} does not exist",
        )
    return {"detail": "OK"}

@router.get("/userm/{email}")
async def get_user_email(session: SessionDep, email: EmailStr):
    if await get_user_by_email(session, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    return {"detail": "OK"}
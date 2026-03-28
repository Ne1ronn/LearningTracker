from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from ..crud.auth.auth_service import register, login, logout, refresh
from ..crud.auth.dependencies import get_current_user, require_role, verify_bot_secret
from ..crud.auth.telegram_token_service import (
    create_telegram_token,
    get_telegram_token,
    delete_telegram_token,
)
from ..crud.auth.token_service import oauth2_scheme
from ..crud.auth.user_repo import (
    get_user_by_username,
    get_user_by_email,
    set_timezone_db,
    change_reminders_enabled_db,
)
from database.setup import SessionDep
from fastapi import APIRouter, Depends, HTTPException, status
from models import UserModel
from schemas.user_schema import (
    UserAddSchema,
    UserTimezoneSchema,
    UserRemindersSchema,
    Token,
    RefreshData,
)

router = APIRouter(tags=["Authentification"])


@router.post("/register")
async def register_user(session: SessionDep, user: UserAddSchema):
    await register(session, user)
    raise HTTPException(
        status_code=status.HTTP_201_CREATED, detail="User added successfully"
    )


@router.post("/login")
async def login_user(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    return await login(session, form_data)


@router.post("/logout")
async def logout_user(session: SessionDep, data: RefreshData):
    await logout(session, data.token)
    return {"detail": "User logged out successfully"}


@router.post("/refresh", status_code=status.HTTP_201_CREATED)
async def refresh_token(session: SessionDep, data: RefreshData):
    return await refresh(session, data.token)


@router.post(
    "/token",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_bot_secret)],
)
async def insert_token(
    session: SessionDep,
    telegram_id: int,
    data: RefreshData,
    user: Annotated[UserModel, Depends(get_current_user)],
    access_token: str = Depends(oauth2_scheme),
):
    await create_telegram_token(session, telegram_id, user, access_token, data.token)
    return {"detail": "Token added successfully"}


@router.get("/token/{telegram_id}", dependencies=[Depends(verify_bot_secret)])
async def get_token(session: SessionDep, telegram_id: int):
    return await get_telegram_token(session, telegram_id)


@router.delete("/token/{telegram_id}", dependencies=[Depends(verify_bot_secret)])
async def delete_token(session: SessionDep, telegram_id: int):
    await delete_telegram_token(session, telegram_id)
    return {"detail": "Token deleted successfully"}


@router.get("/auth/validate")
async def token_check(user: Annotated[UserModel, Depends(get_current_user)]):
    return {"detail": "OK"}


@router.get("/auth/validate/admin")
async def admin_check(admin=Depends(require_role)):
    return {"detail": "OK"}


@router.patch("/user/timezone")
async def set_timezone(
    session: SessionDep,
    timezone_schema: UserTimezoneSchema,
    user: Annotated[UserModel, Depends(get_current_user)],
):
    await set_timezone_db(session, timezone_schema.timezone, user)
    return {"detail": "Timezone set successfully"}


@router.patch("/user/reminders")
async def change_reminders_enabled(
    session: SessionDep,
    reminders_schema: UserRemindersSchema,
    user: Annotated[UserModel, Depends(get_current_user)],
):
    await change_reminders_enabled_db(session, reminders_schema.reminders_enabled, user)
    return {"detail": "Reminders changed successfully"}


@router.get("/user/register/{username}")
async def get_user_for_register(session: SessionDep, username: str):
    if await get_user_by_username(session, username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this name already exists",
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
            detail="User with this email already exists",
        )
    return {"detail": "OK"}

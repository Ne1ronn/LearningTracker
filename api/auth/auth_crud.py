from datetime import datetime
import os
from typing import Annotated

import jwt
from fastapi import HTTPException, status, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pydantic import EmailStr

from api.auth.functions import get_password_hash, create_access_token, verify_password, ACCESS_SECRET_KEY, ALGORITHM, \
    oauth2_scheme, create_refresh_token, REFRESH_SECRET_KEY
from database.setup import SessionDep
from models.refresh_token_model import RefreshTokenModel
from models.telegram_model import TelegramTokenModel
from models.user_model import UserModel
from schemas.user_schema import UserAddSchema, Token, TokenData
from sqlalchemy import select

BOT_SECRET = os.getenv("BOT_SECRET")

async def register(session: SessionDep, user: UserAddSchema):
    if await get_user_by_username(session, user.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this name already exists"
        )

    if await get_user_by_email(session, user.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    hashed_passwd = get_password_hash(user.password)
    new_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hashed_passwd
    )

    session.add(new_user)
    await session.commit()

async def login(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    db_user = await get_user_by_username(session, form_data.username)

    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(username=form_data.username, role=db_user.role)
    refresh_token = await create_refresh_token(session, user_id=db_user.id)
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

async def logout(session: SessionDep, token: str):
    data = await verify_refresh(session, token)
    db_token = data["db_token"]
    db_token.revoked = True
    await session.commit()

async def verify_refresh(session: SessionDep, token: str):
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(401, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(401, detail="Wrong token type")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(401, detail="Empty refresh token")

    try:
        user_id = int(sub)
    except ValueError:
        raise HTTPException(401, detail="Invalid user id")

    jti = payload.get("jti")
    if not jti:
        raise HTTPException(status_code=401, detail="JTI not found")

    db_token = await session.get(RefreshTokenModel, jti)
    user = await get_user_by_id(session, user_id)

    if not db_token:
        raise HTTPException(404, detail="Token not found")
    if db_token.revoked:
        raise HTTPException(401, detail="Token has been revoked")
    if db_token.expires_at < datetime.utcnow():
        raise HTTPException(401, detail="Token has expired")
    if user is None:
        raise HTTPException(404, detail="User not found")
    if db_token.user_id != user.id:
        raise HTTPException(401, detail="Invalid user id")
    return {"user": user, "db_token": db_token}

async def refresh(session: SessionDep, token: str):
    data = await verify_refresh(session, token)
    db_token = data["db_token"]

    db_token.revoked = True
    await session.commit()

    user = data["user"]

    access_token = create_access_token(username=user.username, role=user.role)
    refresh_token = await create_refresh_token(session, user_id=user.id)

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

async def create_telegram_token(session: SessionDep, telegram_id: int, user: UserModel, access_token: str, refresh_token: str):
    stmt = select(TelegramTokenModel).where(TelegramTokenModel.telegram_id == telegram_id)
    result = await session.execute(stmt)
    token = result.scalar_one_or_none()

    if token:
        token.user_id = user.id
        token.access_token = access_token
        token.refresh_token = refresh_token
    else:
        telegram_token = TelegramTokenModel(
            user_id=user.id,
            telegram_id=telegram_id,
            access_token=access_token,
            refresh_token=refresh_token
        )

        session.add(telegram_token)

    await session.commit()

async def get_telegram_token(session: SessionDep, telegram_id: int):
    stmt = select(TelegramTokenModel).where(TelegramTokenModel.telegram_id == telegram_id)
    result = await session.execute(stmt)
    token = result.scalar_one_or_none()

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Token for {telegram_id} telegram_id not found",
        )

    return token

async def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)):
    credential_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credential_exceptions
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credential_exceptions
    user = await get_user_by_username(session, token_data.username)
    if user is None:
        raise credential_exceptions
    return user

async def get_user_by_username(session: SessionDep, username: str):
    stmt = select(UserModel).where(UserModel.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def get_user_by_email(session: SessionDep, email: EmailStr):
    stmt = select(UserModel).where(UserModel.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def get_user_by_id(session: SessionDep, user_id: int):
    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def require_role(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Don't have enough permissions"
        )

async def verify_bot_secret(x_bot_secret: str = Header(...)):
    if x_bot_secret != BOT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid bot secret"
        )
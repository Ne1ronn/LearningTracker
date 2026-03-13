from typing import Annotated
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from .token_service import create_access_token, create_refresh_token, verify_refresh
from .user_repo import get_user_by_username, get_user_by_email
from database.setup import SessionDep
from models import UserModel
from schemas.user_schema import UserAddSchema, Token


password_hash = PasswordHash.recommended()

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

async def refresh(session: SessionDep, token: str):
    data = await verify_refresh(session, token)
    db_token = data["db_token"]

    db_token.revoked = True
    await session.commit()

    user = data["user"]

    access_token = create_access_token(username=user.username, role=user.role)
    refresh_token = await create_refresh_token(session, user_id=user.id)

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(plain, password):
    return password_hash.verify(plain, password)
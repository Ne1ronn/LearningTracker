from typing import Annotated

import jwt
from fastapi import  HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

from api.auth.functions import get_password_hash, create_access_token, verify_password, SECRET_KEY, ALGORITHM, \
    oauth2_scheme
from database.setup import SessionDep
from models.telegram_model import TelegramTokenModel
from models.user_model import UserModel
from schemas.telegram_schema import TelegramTokenAddSchema
from schemas.user_schema import UserAddSchema, Token, TokenData
from sqlalchemy import select

async def register(session: SessionDep, user: UserAddSchema):
    if await get_user_by_username(session, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    hashed_passwd = get_password_hash(user.password)
    new_user = UserModel(
        username = user.username,
        email = user.email,
        hashed_password = hashed_passwd
    )

    session.add(new_user)
    await session.commit()

async def login(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    db_user = await get_user_by_username(session, form_data.username)
    hashed_passwd = get_password_hash(form_data.password)

    if not db_user or not verify_password(form_data.password, hashed_passwd):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": form_data.username})
    return Token(access_token=access_token, token_type="bearer")

async def create_telegram_token(session: SessionDep, data: TelegramTokenAddSchema):
    token = get_telegram_token(session, data.telegram_id)

    if token:
        token.access_token = data.access_token
    else:
        telegram_token = TelegramTokenModel(
            user_id = data.user_id,
            telegram_id = data.telegram_id,
            access_token = data.access_token
        )

        session.add(telegram_token)

    await session.commit()

async def get_telegram_token(session: SessionDep, telegram_id: int):
    stmt = select(TelegramTokenModel).where(TelegramTokenModel.telegram_id == telegram_id)
    result = await session.execute(stmt)
    token = result.scalar_one_or_none()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User with telegram id {telegram_id} unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

async def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)):
    credential_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
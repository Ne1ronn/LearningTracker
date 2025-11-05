from fastapi import  HTTPException, status
from auth.functions import get_password_hash, create_access_token, verify_password
from database.setup import SessionDep
from models.user_model import UserModel
from schemas.user_schema import UserAddSchema, Token
from sqlalchemy import select
from datetime import timedelta

async def register(session: SessionDep, user: UserAddSchema):
    stmt = select(UserModel).where(UserModel.username == user.username)
    result = await session.execute(stmt)
    db_user = result.scalar_one_or_none()
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    hashed_passwd = get_password_hash(user.password)
    new_user = UserModel(
        username = user.username,
        email = user.email,
        hashed_password = hashed_passwd
    )

    session.add(new_user)
    await session.commit()

async def login(session: SessionDep, username: str, passwd: str):
    stmt = select(UserModel).where(UserModel.username == username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    hashed_passwd = get_password_hash(passwd)

    if not user or not verify_password(passwd, hashed_passwd):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": username})
    return Token(access_token=access_token, token_type="bearer")
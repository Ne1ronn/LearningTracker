from fastapi import  HTTPException, status
from api.auth.functions import get_password_hash, create_access_token, verify_password
from database.setup import SessionDep
from models.user_model import UserModel
from schemas.user_schema import UserAddSchema, Token, UserLoginSchema
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

async def login(session: SessionDep, user: UserLoginSchema):
    db_user = get_user_by_username(session, user.username)
    hashed_passwd = get_password_hash(user.password)

    if not db_user or not verify_password(user.password, hashed_passwd):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")

async def get_user_by_username(session: SessionDep, username: str):
    stmt = select(UserModel).where(UserModel.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
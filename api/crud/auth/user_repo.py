from pydantic import EmailStr
from database.setup import SessionDep
from models.user_model import UserModel
from sqlalchemy import select


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

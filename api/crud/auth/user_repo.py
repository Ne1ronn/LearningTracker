from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import HTTPException
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


async def set_timezone_db(session: SessionDep, timezone: str, user: UserModel):
    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        raise HTTPException(status_code=400, detail="Invalid timezone")
    user.timezone = timezone
    await session.commit()


async def change_reminders_enabled_db(
    session: SessionDep, enabled: bool, user: UserModel
):
    user.reminders_enabled = enabled
    await session.commit()

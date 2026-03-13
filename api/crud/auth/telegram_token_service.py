from fastapi import HTTPException, status
from database.setup import SessionDep
from models.telegram_model import TelegramTokenModel
from models.user_model import UserModel
from sqlalchemy import select


async def create_telegram_token(
    session: SessionDep,
    telegram_id: int,
    user: UserModel,
    access_token: str,
    refresh_token: str,
):
    stmt = select(TelegramTokenModel).where(
        TelegramTokenModel.telegram_id == telegram_id
    )
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
            refresh_token=refresh_token,
        )

        session.add(telegram_token)

    await session.commit()


async def get_telegram_token(session: SessionDep, telegram_id: int):
    stmt = select(TelegramTokenModel).where(
        TelegramTokenModel.telegram_id == telegram_id
    )
    result = await session.execute(stmt)
    token = result.scalar_one_or_none()

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Token for {telegram_id} telegram_id not found",
        )

    return token


async def delete_telegram_token(session: SessionDep, telegram_id: int):
    stmt = select(TelegramTokenModel).where(
        TelegramTokenModel.telegram_id == telegram_id
    )
    result = await session.execute(stmt)
    token = result.scalar_one_or_none()

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Token for {telegram_id} telegram_id not found",
        )

    await session.delete(token)
    await session.commit()

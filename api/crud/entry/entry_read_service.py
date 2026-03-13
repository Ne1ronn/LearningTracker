from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from .entry_permessions import can_read_entry
from database.setup import SessionDep
from models import DailyStatsModel, EntryModel, UserModel
from datetime import date
from .entry_queries import apply_filter, apply_sort


async def give_entry(session: SessionDep, entry_id: int, user: UserModel):
    entry = await get_entry_by_id(session, entry_id)
    can_read_entry(entry, user)
    return entry


async def give_all_entry(
    session: SessionDep,
    user: UserModel,
    target_date: date = None,
    private: bool = None,
    min_mood_score: int = None,
    max_mood_score: int = None,
    min_progress_score: int = None,
    max_progress_score: int = None,
    min_learning_hours: float = None,
    max_learning_hours: float = None,
    sort: str = None,
    limit: int = 20,
    offset: int = 0,
):

    stmt = select(EntryModel).where(EntryModel.user_id == user.id)

    stmt = apply_filter(
        stmt,
        target_date,
        private,
        min_mood_score,
        max_mood_score,
        min_progress_score,
        max_progress_score,
        min_learning_hours,
        max_learning_hours,
    )
    stmt = apply_sort(stmt, sort)

    stmt = stmt.offset(offset).limit(limit)
    result = await session.execute(stmt)
    entries = result.scalars().all()

    if not entries:
        return []

    return entries


async def get_entry_count(
    session: SessionDep,
    user: UserModel,
    target_date: date = None,
    private: bool = None,
    min_mood_score: int = None,
    max_mood_score: int = None,
    min_progress_score: int = None,
    max_progress_score: int = None,
    min_learning_hours: float = None,
    max_learning_hours: float = None,
):
    stmt = (
        select(func.count())
        .select_from(EntryModel)
        .where(EntryModel.user_id == user.id)
    )
    stmt = apply_filter(
        stmt,
        target_date,
        private,
        min_mood_score,
        max_mood_score,
        min_progress_score,
        max_progress_score,
        min_learning_hours,
        max_learning_hours,
    )
    total = (await session.execute(stmt)).scalar_one()

    return total


async def get_entry_by_id(session: SessionDep, entry_id: int):
    stmt = (
        select(EntryModel)
        .where((EntryModel.id == entry_id))
        .options(selectinload(EntryModel.topics))
    )

    result = await session.execute(stmt)
    entry = result.scalar_one_or_none()

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry with id {entry_id} not found",
        )

    return entry


async def get_daily_stat(session: SessionDep, user_id: int, entry_date: date):
    stmt = select(DailyStatsModel).where(
        DailyStatsModel.date == entry_date, DailyStatsModel.user_id == user_id
    )
    result = await session.execute(stmt)
    daily_stat = result.scalar_one_or_none()

    return daily_stat

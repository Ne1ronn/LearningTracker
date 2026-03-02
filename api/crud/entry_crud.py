from typing import Union, Annotated

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status, Depends

from api.auth.auth_crud import get_current_user
from database.setup import SessionDep
from models import DailyStatsModel
from models.entry_model import EntryModel
from models.entry_topics_model import entry_topics
from models.topic_model import TopicModel
from models.user_model import UserModel
from schemas.entry_schema import EntryAddSchema, UpdateEntrySchema
from datetime import datetime, date, timedelta


async def missing_topics(session: SessionDep, entry: Union[EntryAddSchema, UpdateEntrySchema]):
    stmt = select(TopicModel).where(TopicModel.id.in_(entry.topic_ids))
    result = await session.execute(stmt)
    topics = result.scalars().all()

    if len(topics) != len(entry.topic_ids):
        found_ids = {topic.id for topic in topics}
        missing = {i for i in entry.topic_ids if not i in found_ids}
        raise HTTPException(
            status_code=404,
            detail=f"Topics not found: {missing}"
        )

    return topics

async def add_entry(session: SessionDep, entry: EntryAddSchema, user: Annotated[UserModel, Depends(get_current_user)]):
    new_entry = EntryModel(
        user_id = user.id,
        title = entry.title,
        description = entry.description,
        tags = entry.tags,
        mood_score = entry.mood_score,
        progress_score = entry.progress_score,
        learning_hours = entry.learning_hours,
        private=entry.private
    )

    if entry.topic_ids:
        topics = await missing_topics(session, entry)
        new_entry.topics.extend(topics)

    session.add(new_entry)
    await session.commit()

    entry_date = new_entry.created_at.date()
    await add_daily_stat(session, user.id, entry_date, entry.learning_hours)

async def add_daily_stat(session: SessionDep, user_id: int, entry_date: date, entry_hours: float):
    stmt = select(DailyStatsModel).where(DailyStatsModel.date == entry_date, DailyStatsModel.user_id == user_id)
    result = await session.execute(stmt)
    daily_stat = result.scalar_one_or_none()

    if not daily_stat:
        new_daily_stat = DailyStatsModel(
            user_id = user_id,
            date = entry_date,
            total_hours=entry_hours,
            entries_count=1
        )
        session.add(new_daily_stat)
    else:
        daily_stat.total_hours += entry_hours
        daily_stat.entries_count += 1

    await session.commit()

async def give_entry(session: SessionDep, entry_id: int, user: Annotated[UserModel, Depends(get_current_user)]):
    entry = await get_entry_by_id(session, entry_id)
    can_read_entry(entry, user)
    return entry

async def give_all_entry(session: SessionDep,
                         user: Annotated[UserModel, Depends(get_current_user)],
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
                         offset: int = 0):

    stmt = select(EntryModel).where(EntryModel.user_id == user.id)

    stmt = apply_filter(stmt, target_date, private, min_mood_score, max_mood_score, min_progress_score, max_progress_score, min_learning_hours, max_learning_hours)
    stmt = apply_sort(stmt, sort)

    stmt = stmt.offset(offset).limit(limit)
    result = await session.execute(stmt)
    entries = result.scalars().all()

    if not entries:
        return []

    return entries

async def update_entry_(session: SessionDep, new_entry: EntryAddSchema, entry_id: int, user: Annotated[UserModel, Depends(get_current_user)]):
    entry = await get_entry_by_id(session, entry_id)
    can_update_entry(entry, user)

    update_dict = new_entry.dict()
    for field, value in update_dict.items():
        setattr(entry, field, value)

    if new_entry.topic_ids:
        topics = await missing_topics(session, new_entry)

        entry.topics = topics

    await session.commit()

async def patch_entry_(session: SessionDep, entry_id: int, patched_entry: UpdateEntrySchema, user: Annotated[UserModel, Depends(get_current_user)]):
    entry = await get_entry_by_id(session, entry_id)
    can_update_entry(entry, user)

    update_dict = patched_entry.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(entry, field, value)

    if patched_entry.topic_ids:
        topics = await missing_topics(session, patched_entry)

        entry.topics = topics

    await session.commit()

async def delete_entry_(session: SessionDep, entry_id: int, user: Annotated[UserModel, Depends(get_current_user)]):
    entry = await get_entry_by_id(session, entry_id)
    can_delete_entry(entry, user)

    await session.delete(entry)
    await session.commit()

async def summary(session: SessionDep, user: Annotated[UserModel, Depends(get_current_user)]):
    stmt = (
        select(
            TopicModel.title,
            func.sum(EntryModel.learning_hours)
        )
        .select_from(TopicModel)
        .join(entry_topics, entry_topics.c.topic_id == TopicModel.id)
        .join(EntryModel, EntryModel.id == entry_topics.c.entry_id                  )
        .where(EntryModel.user_id == user.id)
        .group_by(TopicModel.id)
    )
    result = await session.execute(stmt)
    rows = result.all()

    data = {}
    for title, hours in rows:
        data[title] = hours

    return data

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
            detail=f"Entry with id {entry_id} not found"
        )

    return entry

def can_read_entry(entry: EntryModel, user: UserModel):
    if entry.private and user.id != entry.user_id and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to read this entry"
        )

def can_update_entry(entry: EntryModel, user: UserModel):
    if user.id != entry.user_id and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this entry"
        )

def can_delete_entry(entry: EntryModel, user: UserModel):
    if user.id != entry.user_id and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this entry"
        )

def apply_filter(stmt,
                       target_date: date = None,
                       private: bool = None,
                       min_mood_score: int = None,
                       max_mood_score: int = None,
                       min_progress_score: int = None,
                       max_progress_score: int = None,
                       min_learning_hours: int = None,
                       max_learning_hours: int = None):

    if target_date is not None:
        start = datetime.combine(target_date, datetime.min.time())
        end = start + timedelta(days=1)
        stmt = stmt.where(
            EntryModel.created_at >= start,
            EntryModel.created_at < end,
        )

    if private is not None:
        stmt = stmt.where(EntryModel.private == private)

    if min_mood_score is not None:
        stmt = stmt.where(EntryModel.mood_score >= min_mood_score)
    if max_mood_score is not None:
        stmt = stmt.where(EntryModel.mood_score <= max_mood_score)

    if min_progress_score is not None:
        stmt = stmt.where(EntryModel.progress_score >= min_progress_score)
    if max_progress_score is not None:
        stmt = stmt.where(EntryModel.progress_score <= max_progress_score)

    if min_learning_hours is not None:
        stmt = stmt.where(EntryModel.learning_hours >= min_learning_hours)
    if max_learning_hours is not None:
        stmt = stmt.where(EntryModel.learning_hours <= max_learning_hours)

    return stmt

def apply_sort(stmt, sort: str = None):
    if not sort:
        return stmt.order_by(EntryModel.created_at.desc())

    if sort is not None:
        desc = sort.startswith("-")
        key = sort.lstrip("-")

        field = SORT_FIELDS.get(key)
        if not field:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort field: {key}"
            )

        stmt = stmt.order_by(field.desc() if desc else field.asc())

    return stmt

SORT_FIELDS = {
    "created_at": EntryModel.created_at,
    "mood": EntryModel.mood_score,
    "progress": EntryModel.progress_score,
    "hours": EntryModel.learning_hours,
}
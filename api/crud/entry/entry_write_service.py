from typing import Union
from sqlalchemy import select
from fastapi import HTTPException
from api.crud.entry.entry_permessions import can_update_entry, can_delete_entry
from api.crud.entry.entry_read_service import get_entry_by_id, get_daily_stat
from database.setup import SessionDep
from models import DailyStatsModel, EntryModel, TopicModel, UserModel
from schemas.entry_schema import EntryAddSchema, UpdateEntrySchema
from datetime import date


async def add_entry(session: SessionDep, entry: EntryAddSchema, user: UserModel):
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

    await session.refresh(new_entry)
    entry_date = new_entry.created_at.date()
    await add_daily_stat(session, user.id, entry_date, entry.learning_hours)

async def add_daily_stat(session: SessionDep, user_id: int, entry_date: date, entry_hours: float):
    daily_stat = await get_daily_stat(session, user_id, entry_date)

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

async def update_entry_db(session: SessionDep, new_entry: EntryAddSchema, entry_id: int, user: UserModel):
    entry = await get_entry_by_id(session, entry_id)
    can_update_entry(entry, user)
    old_hours = entry.learning_hours

    update_dict = new_entry.model_dump()
    for field, value in update_dict.items():
        setattr(entry, field, value)

    if new_entry.topic_ids is not None:
        if new_entry.topic_ids:
            topics = await missing_topics(session, new_entry)
            entry.topics = topics
        else:
            entry.topics = []

    entry_hours = new_entry.learning_hours - old_hours
    await update_daily_stat(session, user.id, entry.created_at.date(), entry_hours)

    await session.commit()

async def update_daily_stat(session: SessionDep, user_id: int, entry_date: date, entry_hours: float):
    daily_stat = await get_daily_stat(session, user_id, entry_date)
    daily_stat.total_hours += entry_hours

async def patch_entry_db(session: SessionDep, entry_id: int, patched_entry: UpdateEntrySchema, user: UserModel):
    entry = await get_entry_by_id(session, entry_id)
    can_update_entry(entry, user)
    old_hours = entry.learning_hours

    update_dict = patched_entry.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(entry, field, value)

    if patched_entry.topic_ids is not None:
        if patched_entry.topic_ids:
            topics = await missing_topics(session, patched_entry)
            entry.topics = topics
        else:
            entry.topics = []

    if patched_entry.learning_hours is not None:
        entry_hours = patched_entry.learning_hours - old_hours
        await update_daily_stat(session, user.id, entry.created_at.date(), entry_hours)

    await session.commit()

async def delete_entry_db(session: SessionDep, entry_id: int, user: UserModel):
    entry = await get_entry_by_id(session, entry_id)
    can_delete_entry(entry, user)

    entry_hours = entry.learning_hours

    await session.delete(entry)
    await delete_daily_stat(session, user.id, entry.created_at.date(), entry_hours)

    await session.commit()

async def delete_daily_stat(session: SessionDep, user_id: int, entry_date: date, entry_hours: float):
    daily_stat = await get_daily_stat(session, user_id, entry_date)
    daily_stat.total_hours -= entry_hours
    daily_stat.entries_count -= 1

    if daily_stat.entries_count == 0:
        await session.delete(daily_stat)

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
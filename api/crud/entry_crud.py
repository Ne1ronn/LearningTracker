from typing import Union, Annotated

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status, Depends

from api.auth.auth_crud import get_current_user
from database.setup import SessionDep
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


async def give_entry(session: SessionDep, entry_id: int, user: Annotated[UserModel, Depends(get_current_user)]):
    entry = await get_entry_by_id(session, entry_id)
    can_read_entry(entry, user)
    return entry

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

async def get_entries_by_date_(session: SessionDep, user: Annotated[UserModel, Depends(get_current_user)], date: date):
    start = datetime.combine(date, datetime.min.time())
    end = start + timedelta(days=1)
    stmt = (
        select(EntryModel)
        .where(EntryModel.created_at >= start,
               EntryModel.created_at < end,
               EntryModel.user_id == user.id)
    )

    result = await session.execute(stmt)
    entries = result.scalars().all()

    if entries is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entries with date {date} not found"
        )

    return entries


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
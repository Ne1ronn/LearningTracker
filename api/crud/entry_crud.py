from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from database.setup import SessionDep
from models.entry_model import EntryModel
from models.topic_model import TopicModel
from schemas.entry_schema import EntryAddSchema, UpdateEntrySchema
from typing import List


async def add_entry(session: SessionDep, entry: EntryAddSchema):
    new_entry = EntryModel(
        title = entry.title,
        description = entry.description,
        tags = entry.tags,
        mood_score = entry.mood_score,
        progress_score = entry.progress_score,
        learning_hours = entry.learning_hours
    )

    if entry.topic_ids:
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

        new_entry.topics.extend(topics)

    session.add(new_entry)
    await session.commit()


async def give_entry(session: SessionDep, entry_id: int):
    stmt = select(EntryModel).where(EntryModel.id == entry_id).options(selectinload(EntryModel.topics))
    result = await session.execute(stmt)
    entry = result.scalar_one_or_none()

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry with id {entry_id} not found"
        )

    return entry

async def update_entry_(session: SessionDep, new_entry: EntryAddSchema, entry_id: int):
    entry = give_entry(session, entry_id)

    update_dict = new_entry.dict()
    for field, value in update_dict.items():
        setattr(entry, field, value)

    if new_entry.topic_ids:
        stmt = select(TopicModel).where(TopicModel.id.in_(new_entry.topic_ids))
        result = await session.execute(stmt)
        topics = result.scalars().all()

        if len(topics) != len(new_entry.topic_ids):
            found_ids = {topic.id for topic in topics}
            missing = {i for i in new_entry.topic_ids if not i in found_ids}
            raise HTTPException(
                status_code=404,
                detail=f"Topics not found: {missing}"
            )

        entry.topics = topics

    await session.commit()

async def patch_entry_(session: SessionDep, entry_id: int, patched_entry: UpdateEntrySchema):
    entry = give_entry(session, entry_id)

    update_dict = patched_entry.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(entry, field, value)

    if patched_entry.topic_ids:
        stmt = select(TopicModel).where(TopicModel.id.in_(patched_entry.topic_ids))
        result = await session.execute(stmt)
        topics = result.scalars().all()

        if len(topics) != len(patched_entry.topic_ids):
            found_ids = {topic.id for topic in topics}
            missing = {i for i in patched_entry.topic_ids if not i in found_ids}
            raise HTTPException(
                status_code=404,
                detail=f"Topics not found: {missing}"
            )

        entry.topics = topics

    await session.commit()

async def delete_entry_(session: SessionDep, entry_id: int):
    entry = give_entry(session, entry_id)

    await session.delete(entry)
    await session.commit()
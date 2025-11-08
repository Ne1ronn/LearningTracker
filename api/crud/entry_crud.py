from typing import Union, Annotated

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status, Depends

from api.auth.register import get_current_user
from database.setup import SessionDep
from models.entry_model import EntryModel
from models.topic_model import TopicModel
from models.user_model import UserModel
from schemas.entry_schema import EntryAddSchema, UpdateEntrySchema


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
        learning_hours = entry.learning_hours
    )

    if entry.topic_ids:
        topics = await missing_topics(session, entry)
        new_entry.topics.extend(topics)

    session.add(new_entry)
    await session.commit()


async def give_entry(session: SessionDep, entry_id: int, user: Annotated[UserModel, Depends(get_current_user)]):
    stmt = (
        select(EntryModel)
        .where((EntryModel.id == entry_id) & (user.id == EntryModel.user_id))
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

async def update_entry_(session: SessionDep, new_entry: EntryAddSchema, entry_id: int, user: Annotated[UserModel, Depends(get_current_user)]):
    entry = await give_entry(session, entry_id, user)
    update_dict = new_entry.dict()
    entry.user_id = user.id
    for field, value in update_dict.items():
        setattr(entry, field, value)

    if new_entry.topic_ids:
        topics = await missing_topics(session, new_entry)

        entry.topics = topics

    await session.commit()

async def patch_entry_(session: SessionDep, entry_id: int, patched_entry: UpdateEntrySchema, user: Annotated[UserModel, Depends(get_current_user)]):
    entry = await give_entry(session, entry_id, user)
    update_dict = patched_entry.dict(exclude_unset=True)
    entry.user_id = user.id
    for field, value in update_dict.items():
        setattr(entry, field, value)

    if patched_entry.topic_ids:
        topics = await missing_topics(session, patched_entry)

        entry.topics = topics

    await session.commit()

async def delete_entry_(session: SessionDep, entry_id: int, user: Annotated[UserModel, Depends(get_current_user)]):
    entry = await give_entry(session, entry_id, user)
    if entry.user_id == user.id:
        await session.delete(entry)
        await session.commit()
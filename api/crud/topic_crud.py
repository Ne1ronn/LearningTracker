from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from database.setup import SessionDep
from models.topic_model import TopicModel
from schemas.topic_schema import TopicAddSchema


async def add_topic(session: SessionDep, topic: TopicAddSchema):
    new_topic = TopicModel(
        title = topic.title,
        skill = topic.skill,
        is_active = topic.is_active
    )

    session.add(new_topic)
    await session.commit()

async def give_topic(session: SessionDep, topic_id: int):
    stmt = select(TopicModel).where(TopicModel.id == topic_id)
    result = await session.execute(stmt)
    topic = result.scalar_one_or_none()

    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic with id {topic_id} not found"
        )

    return topic

async def update_topic_(session: SessionDep, new_topic: TopicAddSchema, topic_id: int):
    stmt = select(TopicModel).where(TopicModel.id == topic_id)
    result = await session.execute(stmt)
    topic = result.scalar_one_or_none()

    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic with id {topic_id} not found"
        )

    topic.title = new_topic.title
    topic.skill = new_topic.skill
    topic.is_active = new_topic.is_active
    topic.entries = new_topic.entries

async def delete_topic_(session: SessionDep, topic_id: int):
    stmt = select(TopicModel).where(TopicModel.id == topic_id)
    result = await session.execute(stmt)
    topic = result.scalar_one_or_none()

    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic with id {topic_id} not found"
        )

    await session.delete(topic)
    await session.commit()
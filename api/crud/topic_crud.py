from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from database.setup import SessionDep
from models.topic_model import TopicModel
from schemas.topic_schema import TopicAddSchema, UpdateTopicSchema


async def add_topic(session: SessionDep, topic: TopicAddSchema):
    new_topic = TopicModel(
        title = topic.title,
        skill = topic.skill,
        need = topic.need,
        progress_score = topic.progress_score,
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

    updated_dic = new_topic.dict()
    for field, value in updated_dic.items():
        setattr(topic, field, value)

    await session.commit()

async def patch_topic_(session: SessionDep, patched_topic: UpdateTopicSchema, topic_id: int):
    stmt = select(TopicModel).where(TopicModel.id == topic_id)
    result = await session.execute(stmt)
    topic = result.scalar_one_or_none()

    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic with id {topic_id} not found"
        )

    updated_dic = patched_topic.dict(exclude_unset=True)
    for field, value in updated_dic.items():
        setattr(topic, field, value)

    await session.commit()

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
from sqlalchemy import select
from fastapi import HTTPException, status
from database.setup import SessionDep
from models import UserModel
from models.topic_model import TopicModel
from schemas.topic_schema import TopicAddSchema, UpdateTopicSchema


async def add_topic(session: SessionDep, topic: TopicAddSchema, user: UserModel):
    new_topic = TopicModel(
        user_id=user.id,
        title=topic.title,
        skill=topic.skill,
        description=topic.description,
        category=topic.category,
        is_active=topic.is_active,
    )

    session.add(new_topic)
    await session.commit()


async def give_topic(session: SessionDep, topic_id: int, user: UserModel):
    topic = await get_topic_by_id(session, topic_id)
    can_topic(topic, user)
    return topic


async def get_all_topics_db(
    session: SessionDep, user: UserModel, limit: int = 10, offset: int = 0
):
    stmt = (
        select(TopicModel)
        .where(TopicModel.user_id == user.id)
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(stmt)
    topics = result.scalars().all()

    return topics


async def update_topic_db(
    session: SessionDep, new_topic: TopicAddSchema, topic_id: int, user: UserModel
):
    topic = await get_topic_by_id(session, topic_id)
    can_topic(topic, user)

    updated_dic = new_topic.model_dump()
    for field, value in updated_dic.items():
        setattr(topic, field, value)

    await session.commit()


async def patch_topic_db(
    session: SessionDep,
    patched_topic: UpdateTopicSchema,
    topic_id: int,
    user: UserModel,
):
    topic = await get_topic_by_id(session, topic_id)
    can_topic(topic, user)

    updated_dic = patched_topic.model_dump(exclude_unset=True)
    for field, value in updated_dic.items():
        setattr(topic, field, value)

    await session.commit()


async def delete_topic_db(session: SessionDep, topic_id: int, user: UserModel):
    topic = await get_topic_by_id(session, topic_id)
    can_topic(topic, user)

    await session.delete(topic)
    await session.commit()


async def get_topic_by_id(session: SessionDep, topic_id: int):
    stmt = select(TopicModel).where(TopicModel.id == topic_id)
    result = await session.execute(stmt)
    topic = result.scalar_one_or_none()

    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic with id {topic_id} not found",
        )

    return topic


def can_topic(topic: TopicModel, user: UserModel):
    if user.id != topic.user_id and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to read this topic",
        )

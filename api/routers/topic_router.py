from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from models import UserModel
from ..crud.auth.dependencies import get_current_user
from api.crud.topic.topic_crud import (
    add_topic,
    give_topic,
    update_topic_db,
    patch_topic_db,
    delete_topic_db,
    get_all_topics_db,
)
from database.setup import SessionDep
from schemas.topic_schema import TopicAddSchema, UpdateTopicSchema

router = APIRouter(tags=["Tracker Topics"])


@router.post("/topics")
async def insert_topic(
    session: SessionDep,
    topic: TopicAddSchema,
    user: Annotated[UserModel, Depends(get_current_user)],
):
    await add_topic(session, topic, user)
    raise HTTPException(
        status_code=status.HTTP_201_CREATED, detail="Topic added successfully"
    )


@router.get("/topics/{topic_id}")
async def get_topic(
    session: SessionDep,
    topic_id: int,
    user: Annotated[UserModel, Depends(get_current_user)],
):
    return await give_topic(session, topic_id, user)


@router.get("/topics")
async def get_all_topics(
    session: SessionDep, user: Annotated[UserModel, Depends(get_current_user)]
):
    return await get_all_topics_db(session, user)


@router.put("/topics/{topic_id}")
async def update_topic(
    session: SessionDep,
    topic: TopicAddSchema,
    topic_id: int,
    user: Annotated[UserModel, Depends(get_current_user)],
):
    await update_topic_db(session, topic, topic_id, user)
    return {"message": "Topic updated successfully"}


@router.patch("/topics/{topic_id}")
async def patch_topic(
    session: SessionDep,
    patched_topic: UpdateTopicSchema,
    topic_id: int,
    user: Annotated[UserModel, Depends(get_current_user)],
):
    await patch_topic_db(session, patched_topic, topic_id, user)
    return {"message": "Topic updated successfully"}


@router.delete("/topics/{topic_id}")
async def delete_topic(
    session: SessionDep,
    topic_id: int,
    user: Annotated[UserModel, Depends(get_current_user)],
):
    await delete_topic_db(session, topic_id, user)
    return {"message": "Topic deleted successfully"}

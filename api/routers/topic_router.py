from fastapi import APIRouter, Depends, status, HTTPException

from ..crud.auth.dependencies import require_role, get_current_user
from api.crud.topic_crud import add_topic, give_topic, update_topic_, patch_topic_, delete_topic_, get_all_topics_db
from database.setup import SessionDep
from schemas.topic_schema import TopicAddSchema, UpdateTopicSchema

router = APIRouter(tags=["Tracker Topics"])

@router.post("/topics", dependencies=[Depends(require_role)])
async def insert_topic(session: SessionDep, topic: TopicAddSchema):
    await add_topic(session, topic)
    raise HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="Topic added successfully"
    )

@router.get("/topics/{topic_id}", dependencies=[Depends(get_current_user)])
async def get_topic(session: SessionDep, topic_id: int):
    return await give_topic(session, topic_id)

@router.get("/topics", dependencies=[Depends(get_current_user)])
async def get_all_topics(session: SessionDep):
    return await get_all_topics_db(session)

@router.put("/topics/{topic_id}", dependencies=[Depends(require_role)])
async def update_topic(session: SessionDep, topic: TopicAddSchema, topic_id: int):
    await update_topic_(session, topic, topic_id)
    return {"message": "Topic updated successfully"}

@router.patch("/topics/{topic_id}", dependencies=[Depends(require_role)])
async def patch_topic(session: SessionDep, patched_topic: UpdateTopicSchema, topic_id: int):
    await patch_topic_(session, patched_topic, topic_id)
    return {"message": "Topic updated successfully"}

@router.delete("/topics/{topic_id}", dependencies=[Depends(require_role)])
async def delete_topic(session: SessionDep, topic_id: int):
    await delete_topic_(session, topic_id)
    return {"message": "Topic deleted successfully"}
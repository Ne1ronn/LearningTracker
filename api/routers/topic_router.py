from fastapi import APIRouter, status
from api.crud.topic_crud import add_topic, give_topic, update_topic_, delete_topic_
from database.setup import SessionDep
from models.topic_model import TopicModel
from schemas.topic_schema import TopicAddSchema

router = APIRouter(tags=["Tracker Topics"])

@router.post("/topics")
async def insert_topic(session: SessionDep, topic: TopicAddSchema):
    await add_topic(session, topic)
    return {"message": "Topic added successfully"}

@router.get("/topic/{topic_id}")
async def get_topic(session: SessionDep, topic_id: int):
    return await give_topic(session, topic_id)

@router.put("/topic/{topic_id}")
async def update_topic(session: SessionDep, topic: TopicAddSchema, topic_id: int):
    await update_topic_(session, topic, topic_id)
    return {"message": "Topic updated successfully"}

@router.delete("/topic/{topic_id}")
async def delete_topic(session: SessionDep, topic_id: int):
    await delete_topic_(session, topic_id)
    return {"message": "Topic deleted successfully"}
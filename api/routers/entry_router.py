from fastapi import APIRouter, status

from api.crud.entry_crud import add_entry, give_entry, update_entry_, delete_entry_
from database.setup import SessionDep
from schemas.entry_schema import EntryAddSchema

router = APIRouter(tags=["Entry Tracking"])

@router.post("/entries")
async def insert_entry(session: SessionDep, entry: EntryAddSchema):
    await add_entry(session, entry)
    return {"message": "Entry added successfully"}

@router.get("/entries/{id}")
async def get_entry(session: SessionDep, id: int):
    return await give_entry(session, id)

@router.put("/entries/{id}")
async def update_entry(session: SessionDep, entry: EntryAddSchema, id: int):
    await update_entry_(session, entry, id)
    return {"message": "Entry updated successfully"}

@router.delete("/entries/{id}")
async def delete_entry(session: SessionDep, id: int):
    await delete_entry_(session, id)
    return {"message": "Entry deleted successfully"}
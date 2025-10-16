from fastapi import APIRouter, status

from api.crud.entry_crud import add_entry, give_entry, update_entry_, delete_entry_
from database.setup import SessionDep
from schemas.entry_schema import EntryAddSchema, EntrySchema

router = APIRouter(tags=["Entry Tracking"])

@router.post("/entries")
async def insert_entry(session: SessionDep, entry: EntryAddSchema):
    await add_entry(session, entry)
    return {"message": "Entry added successfully"}

@router.get("/entries/{entry_id}", response_model=EntrySchema)
async def get_entry(session: SessionDep, entry_id: int):
    entry = await give_entry(session, entry_id)
    return EntrySchema.from_orm(entry)

@router.put("/entries/{entry_id}")
async def update_entry(session: SessionDep, entry: EntryAddSchema, entry_id: int):
    await update_entry_(session, entry, entry_id)
    return {"message": "Entry updated successfully"}

@router.delete("/entries/{entry_id}")
async def delete_entry(session: SessionDep, entry_id: int):
    await delete_entry_(session, entry_id)
    return {"message": "Entry deleted successfully"}
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from api.crud.entry_crud import (add_entry, give_entry, update_entry_, patch_entry_, delete_entry_, summary, can_update_entry, can_delete_entry, get_entry_by_id)
from api.auth.auth_crud import get_current_user
from database.setup import SessionDep
from models import EntryModel
from models.user_model import UserModel
from schemas.entry_schema import EntryAddSchema, EntrySchema, UpdateEntrySchema

router = APIRouter(tags=["Entry Tracking"])

@router.post("/entries")
async def insert_entry(session: SessionDep, entry: EntryAddSchema, user: Annotated[UserModel, Depends(get_current_user)]):
    await add_entry(session, entry, user)
    raise HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="Entry added successfully"
    )

@router.get("/entries/summary")
async def hours_summary(session: SessionDep, user: Annotated[UserModel, Depends(get_current_user)]):
    return await summary(session, user)

@router.get("/entries/{entry_id}", response_model=EntrySchema)
async def get_entry(session: SessionDep, entry_id: int, user: Annotated[UserModel, Depends(get_current_user)]):
    return await give_entry(session, entry_id, user)

@router.put("/entries/{entry_id}")
async def update_entry(session: SessionDep, entry: EntryAddSchema, entry_id: int, user: Annotated[UserModel, Depends(get_current_user)]):
    await update_entry_(session, entry, entry_id, user)
    return {"message": "Entry updated successfully"}

@router.patch("/entries/{entry_id}")
async def patch_entry(session: SessionDep, patched_entry: UpdateEntrySchema, entry_id: int, user: Annotated[UserModel, Depends(get_current_user)]):
    await patch_entry_(session, entry_id, patched_entry, user)
    return {"message": "Entry updated successfully"}

@router.delete("/entries/{entry_id}")
async def delete_entry(session: SessionDep, entry_id: int, user: Annotated[UserModel, Depends(get_current_user)]):
    await delete_entry_(session, entry_id, user)
    return {"message": "Entry deleted successfully"}

@router.get("/entries/{entry_id}/edit")
async def can_edit(session: SessionDep, entry_id: int, user: Annotated[UserModel, Depends(get_current_user)]):
    entry = await get_entry_by_id(session, entry_id)
    can_update_entry(entry, user)
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from api.crud.entry_crud import (add_entry, give_all_entry, give_entry, update_entry_, patch_entry_, delete_entry_,
                                 summary, can_update_entry, get_entry_by_id, get_weekly_stats)
from api.auth.auth_crud import get_current_user
from database.setup import SessionDep
from models.user_model import UserModel
from schemas.entry_schema import EntryAddSchema, EntrySchema, UpdateEntrySchema
from datetime import date

from schemas.weekly_stats_schema import WeeklyStatsResponseSchema

router = APIRouter(tags=["Entry Tracking"])

@router.post("/entries")
async def insert_entry(session: SessionDep, entry: EntryAddSchema, user: Annotated[UserModel, Depends(get_current_user)]):
    await add_entry(session, entry, user)
    raise HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="Entry added successfully"
    )

@router.get("/entries")
async def get_all_entries(session: SessionDep,
                         user: Annotated[UserModel, Depends(get_current_user)],
                         target_date: date = None,
                         private: bool = None,
                         min_mood_score: int = None,
                         max_mood_score: int = None,
                         min_progress_score: int = None,
                         max_progress_score: int = None,
                         min_learning_hours: float = None,
                         max_learning_hours: float = None,
                         sort: str = None,
                         limit: int = 20,
                         offset: int = 0):

    return await give_all_entry(session, user, target_date, private, min_mood_score, max_mood_score, min_progress_score, max_progress_score, min_learning_hours, max_learning_hours, sort, limit, offset)

@router.get("/entries/summary")
async def hours_summary(session: SessionDep, user: Annotated[UserModel, Depends(get_current_user)]):
    return await summary(session, user)

@router.get("/entries/{entry_id}", response_model=EntrySchema)
async def get_entry(session: SessionDep, entry_id: int, user: Annotated[UserModel, Depends(get_current_user)]):
    return await give_entry(session, entry_id, user)

@router.get("/entries/stats/weekly", response_model=WeeklyStatsResponseSchema)
async def weekly_stats(session: SessionDep, user: Annotated[UserModel, Depends(get_current_user)]):
    return await get_weekly_stats(session, user)

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
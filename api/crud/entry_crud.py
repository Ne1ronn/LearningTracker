from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from database.setup import SessionDep
from models.entry_model import EntryModel
from schemas.entry_schema import EntryAddSchema


async def add_entry(session: SessionDep, entry: EntryAddSchema):
    new_entry = EntryModel(
        title = entry.title,
        description = entry.description,
        tags = entry.tags,
        created_at = entry.created_at,
        mood_score = entry.mood_score
    )

    session.add(new_entry)
    await session.commit()

async def give_entry(session: SessionDep, entry_id: int):
    stmt = (
        select(EntryModel).where(EntryModel.id == entry_id)
    )
    result = await session.execute(stmt)
    entry = result.scalar_one_or_none()

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry with id {entry_id} not found"
        )

    return entry

async def update_entry(session: SessionDep, new_entry: EntryAddSchema, entry_id: int):
    stmt = (
        select(EntryModel).where(EntryModel.id == entry_id)
    )
    result = await session.execute(stmt)
    entry = result.scalar_one_or_none()

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry with id {entry_id} not found"
        )

    entry.title = new_entry.title
    entry.description = new_entry.description
    entry.tags = new_entry.tags
    entry.created_at = new_entry.created_at
    entry.mood_score = new_entry.mood_score

    await session.commit()

async def delete_entry(session: SessionDep, entry_id: int):
    stmt = (
        select(EntryModel).where(EntryModel.id == entry_id)
    )
    result = await session.execute(stmt)
    entry = result.scalar_one_or_none()

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry with id {entry_id} not found"
        )

    await session.delete(entry)
    await session.commit()
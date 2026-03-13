from fastapi import HTTPException, status
from models import EntryModel, UserModel


def can_read_entry(entry: EntryModel, user: UserModel):
    if entry.private and user.id != entry.user_id and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to read this entry",
        )


def can_update_entry(entry: EntryModel, user: UserModel):
    if user.id != entry.user_id and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this entry",
        )


def can_delete_entry(entry: EntryModel, user: UserModel):
    if user.id != entry.user_id and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this entry",
        )

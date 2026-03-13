from fastapi import HTTPException, status
from models import EntryModel
from datetime import datetime, date, timedelta


def apply_filter(
    stmt,
    target_date: date = None,
    private: bool = None,
    min_mood_score: int = None,
    max_mood_score: int = None,
    min_progress_score: int = None,
    max_progress_score: int = None,
    min_learning_hours: int = None,
    max_learning_hours: int = None,
):

    if target_date is not None:
        start = datetime.combine(target_date, datetime.min.time())
        end = start + timedelta(days=1)
        stmt = stmt.where(
            EntryModel.created_at >= start,
            EntryModel.created_at < end,
        )

    if private is not None:
        stmt = stmt.where(EntryModel.private == private)

    if min_mood_score is not None:
        stmt = stmt.where(EntryModel.mood_score >= min_mood_score)
    if max_mood_score is not None:
        stmt = stmt.where(EntryModel.mood_score <= max_mood_score)

    if min_progress_score is not None:
        stmt = stmt.where(EntryModel.progress_score >= min_progress_score)
    if max_progress_score is not None:
        stmt = stmt.where(EntryModel.progress_score <= max_progress_score)

    if min_learning_hours is not None:
        stmt = stmt.where(EntryModel.learning_hours >= min_learning_hours)
    if max_learning_hours is not None:
        stmt = stmt.where(EntryModel.learning_hours <= max_learning_hours)

    return stmt


def apply_sort(stmt, sort: str = None):
    if not sort:
        return stmt.order_by(EntryModel.created_at.desc())

    if sort is not None:
        desc = sort.startswith("-")
        key = sort.lstrip("-")

        field = SORT_FIELDS.get(key)
        if not field:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort field: {key}",
            )

        stmt = stmt.order_by(field.desc() if desc else field.asc())

    return stmt


SORT_FIELDS = {
    "created_at": EntryModel.created_at,
    "mood": EntryModel.mood_score,
    "progress": EntryModel.progress_score,
    "hours": EntryModel.learning_hours,
}

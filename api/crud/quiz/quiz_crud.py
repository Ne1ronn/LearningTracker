import datetime
from datetime import UTC, timedelta
from sqlalchemy import select
from fastapi import HTTPException, status
from database.setup import SessionDep
from models import UserModel, EntryModel
from models import QuizModel
from schemas.quiz_schema import QuizAddSchema, QuizUpdateSchema


async def create_quiz(session: SessionDep, quiz: QuizAddSchema, user: UserModel):
    stmt = select(EntryModel).where(
        EntryModel.id == quiz.entry_id, EntryModel.user_id == user.id
    )
    result = await session.execute(stmt)
    entry = result.scalar_one_or_none()

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Entry not found"
        )

    quiz_model = QuizModel(
        entry_id=quiz.entry_id,
        question=quiz.question,
        answer=quiz.answer,
        next_review_at=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=1),
    )
    session.add(quiz_model)
    await session.commit()


async def get_quiz_by_id(session: SessionDep, quiz_id: int, user: UserModel):
    stmt = (
        select(QuizModel)
        .where(QuizModel.id == quiz_id)
        .join(EntryModel)
        .where(EntryModel.user_id == user.id)
    )
    result = await session.execute(stmt)
    quiz = result.scalar_one_or_none()

    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Quiz not found"
        )

    return quiz


async def get_quizzes_db(session: SessionDep, user: UserModel):
    stmt = select(QuizModel).join(EntryModel).where(EntryModel.user_id == user.id)
    result = await session.execute(stmt)
    quizzes = result.scalars().all()
    return quizzes


async def patch_quiz_db(
    session: SessionDep, quiz_id: int, patched_quiz: QuizUpdateSchema, user: UserModel
):
    quiz = await get_quiz_by_id(session, quiz_id, user)

    updated_dict = patched_quiz.model_dump(exclude_unset=True)
    for field, value in updated_dict.items():
        setattr(quiz, field, value)
    await session.commit()


async def delete_quiz_db(session: SessionDep, quiz_id: int, user: UserModel):
    quiz = await get_quiz_by_id(session, quiz_id, user)
    await session.delete(quiz)
    await session.commit()


async def change_quiz(session: SessionDep, quiz_id: int, result: str, user: UserModel):
    quiz = await get_quiz_by_id(session, quiz_id, user)
    now = datetime.now(UTC)

    if result == "know":
        review_step = quiz.review_step

        if not review_step:
            quiz.next_review_at = now + timedelta(days=1)
        elif review_step == 1:
            quiz.next_review_at = now + timedelta(days=3)
        elif review_step == 2:
            quiz.next_review_at = now + timedelta(days=7)
        elif review_step == 3:
            quiz.is_active = False

        if review_step != 3:
            quiz.review_step += 1

    elif result == "do_not_know":
        quiz.review_step = 0
        quiz.next_review_at = now + timedelta(days=1)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid quiz review result",
        )

    quiz.awaiting_response = False
    await session.commit()

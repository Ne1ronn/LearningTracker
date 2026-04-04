from sqlalchemy import select
from fastapi import HTTPException, status
from database.setup import SessionDep
from models import UserModel, EntryModel
from models import QuizModel
from schemas.quiz_schema import QuizAddSchema, QuizUpdateSchema


async def add_quiz(session: SessionDep, quiz: QuizAddSchema, user: UserModel):
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


async def patch_quiz(
    session: SessionDep, quiz_id: int, patched_quiz: QuizUpdateSchema, user: UserModel
):
    quiz = await get_quiz_by_id(session, quiz_id, user)

    updated_dict = patched_quiz.model_dump(exclude_unset=True)
    for field, value in updated_dict.items():
        setattr(quiz, field, value)
    await session.commit()


async def delete_quiz(session: SessionDep, quiz_id: int, user: UserModel):
    quiz = await get_quiz_by_id(session, quiz_id, user)
    await session.delete(quiz)
    await session.commit()

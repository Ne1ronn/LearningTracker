from typing import Annotated
from fastapi import APIRouter, Depends, status
from schemas.quiz_schema import QuizAddSchema, QuizUpdateSchema
from ..crud.auth.dependencies import get_current_user
from database.setup import SessionDep
from models.user_model import UserModel
from ..crud.quiz.quiz_crud import (
    create_quiz,
    get_quiz_by_id,
    get_quizzes_db,
    delete_quiz_db,
    patch_quiz_db,
    change_quiz,
)

router = APIRouter(tags=["Quiz Tracking"])


@router.post("/quizzes", status_code=status.HTTP_201_CREATED)
async def add_quiz(
    session: SessionDep,
    quiz: QuizAddSchema,
    user: Annotated[UserModel, Depends(get_current_user)],
):
    await create_quiz(session, quiz, user)
    return {"detail": "Quiz added successfully"}


@router.get("/quizzes/{quiz_id}", status_code=status.HTTP_200_OK)
async def get_quiz(
    session: SessionDep,
    quiz_id: int,
    user: Annotated[UserModel, Depends(get_current_user)],
):
    return await get_quiz_by_id(session, quiz_id, user)


@router.get("/quizzes", status_code=status.HTTP_200_OK)
async def get_quizzes(
    session: SessionDep, user: Annotated[UserModel, Depends(get_current_user)]
):
    return await get_quizzes_db(session, user)


@router.patch("/quizzes/{quiz_id}", status_code=status.HTTP_200_OK)
async def patch_quiz(
    session: SessionDep,
    quiz_id: int,
    patched_quiz: QuizUpdateSchema,
    user: Annotated[UserModel, Depends(get_current_user)],
):
    await patch_quiz_db(session, quiz_id, patched_quiz, user)
    return {"detail": "Quiz changed successfully"}


@router.delete("/quizzes/{quiz_id}", status_code=status.HTTP_200_OK)
async def delete_quiz(
    session: SessionDep,
    quiz_id: int,
    user: Annotated[UserModel, Depends(get_current_user)],
):
    await delete_quiz_db(session, quiz_id, user)
    return {"detail": "Quiz deleted successfully"}


@router.patch("/quizzes/status/{quiz_id}", status_code=status.HTTP_200_OK)
async def change_quiz_status(
    session: SessionDep,
    quiz_id: int,
    result: str,
    user: Annotated[UserModel, Depends(get_current_user)],
):
    await change_quiz(session, quiz_id, result, user)

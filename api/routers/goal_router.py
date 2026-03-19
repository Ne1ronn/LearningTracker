from dataclasses import asdict
from typing import Annotated
from fastapi import APIRouter, Depends, status
from schemas.goal_schema import GoalAddSchema, GoalUpdateSchema, GoalResponseSchema
from ..crud.auth.dependencies import get_current_user
from database.setup import SessionDep
from models.user_model import UserModel
from ..crud.goal.goal_crud import (
    add_goal,
    get_goal_by_id,
    get_goals_db,
    patch_goal_db,
    delete_goal_db,
    get_goal_progress,
)

router = APIRouter(tags=["Goals"])


@router.post("/goals", status_code=status.HTTP_201_CREATED)
async def insert_goal(
    session: SessionDep,
    goal: GoalAddSchema,
    user: Annotated[UserModel, Depends(get_current_user)],
):
    await add_goal(session, goal, user)
    return {"detail": "Goal added successfully"}


@router.get("/goals/{goal_id}", status_code=status.HTTP_200_OK)
async def get_goal(
    session: SessionDep,
    goal_id: int,
    user: Annotated[UserModel, Depends(get_current_user)],
):
    return await get_goal_by_id(session, goal_id, user)


@router.get("/goals", status_code=status.HTTP_200_OK)
async def get_goals(
    session: SessionDep, user: Annotated[UserModel, Depends(get_current_user)]
):
    return await get_goals_db(session, user)


@router.patch("/goals/{goal_id}", status_code=status.HTTP_200_OK)
async def patch_goal(
    session: SessionDep,
    patched_goal: GoalUpdateSchema,
    goal_id: int,
    user: Annotated[UserModel, Depends(get_current_user)],
):
    await patch_goal_db(session, patched_goal, goal_id, user)
    return {"detail": "Goal patched successfully"}


@router.delete("/goals/{goal_id}", status_code=status.HTTP_200_OK)
async def delete_goal(
    session: SessionDep,
    goal_id: int,
    user: Annotated[UserModel, Depends(get_current_user)],
):
    await delete_goal_db(session, goal_id, user)
    return {"detail": "Goal deleted successfully"}


@router.get("/goals/{goal_id}/stats", response_model=GoalResponseSchema)
async def get_goal_stats(
    session: SessionDep,
    goal_id: int,
    user: Annotated[UserModel, Depends(get_current_user)],
):
    return await get_goal_progress(session, goal_id, user)

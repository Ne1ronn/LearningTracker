from sqlalchemy import select
from fastapi import HTTPException, status
from api.crud.topic.topic_crud import get_topic_by_id
from database.setup import SessionDep
from models import UserModel
from models.goal_model import GoalModel
from schemas.goal_schema import GoalAddSchema, GoalUpdateSchema


async def add_goal(session: SessionDep, goal: GoalAddSchema, user: UserModel):
    await get_topic_by_id(session, goal.topic_id)

    db_goal = GoalModel(
        user_id=user.id,
        topic_id=goal.topic_id,
        target_hours=goal.target_hours,
        target_date=goal.target_date,
    )
    session.add(db_goal)
    await session.commit()


async def get_goal_by_id(session: SessionDep, goal_id: int, user: UserModel):
    stmt = select(GoalModel).where(
        GoalModel.id == goal_id, GoalModel.user_id == user.id
    )
    result = await session.execute(stmt)
    goal = result.scalar_one_or_none()

    if goal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found"
        )

    return goal


async def get_goals_db(session: SessionDep, user: UserModel):
    stmt = select(GoalModel).where(GoalModel.user_id == user.id)
    result = await session.execute(stmt)
    goals = result.scalars().all()
    return goals


async def patch_goal_db(
    session: SessionDep, patched_goal: GoalUpdateSchema, goal_id: int, user: UserModel
):
    goal = await get_goal_by_id(session, goal_id, user)

    updated_dic = patched_goal.model_dump(exclude_unset=True)
    for field, value in updated_dic.items():
        setattr(goal, field, value)

    await session.commit()


async def delete_goal_db(session: SessionDep, goal_id: int, user: UserModel):
    goal = await get_goal_by_id(session, goal_id, user)
    await session.delete(goal)
    await session.commit()

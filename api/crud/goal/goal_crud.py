from datetime import date, timedelta

from sqlalchemy import select, func
from fastapi import HTTPException, status
from api.crud.topic.topic_crud import get_topic_by_id, give_topic
from database.setup import SessionDep
from models import UserModel, EntryModel, TopicModel, entry_topics
from models.goal_model import GoalModel
from schemas.goal_schema import GoalAddSchema, GoalUpdateSchema, GoalResponseSchema


async def create_goal(session: SessionDep, new_goal: GoalAddSchema, user: UserModel):
    await give_topic(session, new_goal.topic_id, user)
    stmt = select(GoalModel).where(
        GoalModel.topic_id == new_goal.topic_id, GoalModel.user_id == user.id
    )
    result = await session.execute(stmt)
    goals = result.scalars().all()

    for goal in goals:
        hours_stmt = (
            select(func.sum(EntryModel.learning_hours))
            .select_from(TopicModel)
            .where(TopicModel.id == goal.topic_id, TopicModel.user_id == user.id)
            .join(entry_topics, entry_topics.c.topic_id == TopicModel.id)
            .join(EntryModel, EntryModel.id == entry_topics.c.entry_id)
            .where(
                EntryModel.user_id == user.id,
                EntryModel.created_at >= goal.started_at,
                EntryModel.created_at < goal.target_date + timedelta(days=1),
            )
        )

        result = await session.execute(hours_stmt)
        hours_done = result.scalar() or 0

        if hours_done >= goal.target_hours or (
            hours_done < goal.target_hours and goal.target_date <= date.today()
        ):
            continue
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Active goal for this topic already exists",
            )

    db_goal = GoalModel(
        user_id=user.id,
        topic_id=new_goal.topic_id,
        target_hours=new_goal.target_hours,
        target_date=new_goal.target_date,
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


async def get_goal_progress(session: SessionDep, goal_id: int, user: UserModel):
    goal = await get_goal_by_id(session, goal_id, user)
    stmt = (
        select(func.sum(EntryModel.learning_hours))
        .select_from(TopicModel)
        .where(TopicModel.id == goal.topic_id, TopicModel.user_id == user.id)
        .join(entry_topics, entry_topics.c.topic_id == TopicModel.id)
        .join(EntryModel, EntryModel.id == entry_topics.c.entry_id)
        .where(
            EntryModel.user_id == user.id,
            EntryModel.created_at >= goal.started_at,
            EntryModel.created_at < goal.target_date + timedelta(days=1),
        )
    )

    result = await session.execute(stmt)
    hours_done = result.scalar() or 0
    days_passed = (date.today() - goal.started_at.date()).days
    days_left = (
        (goal.target_date - date.today()).days if goal.target_date > date.today() else 0
    )
    hours_left = (
        (goal.target_hours - hours_done) if goal.target_hours > hours_done else 0
    )

    if hours_left == 0:
        return GoalResponseSchema(
            topic_id=goal.topic_id,
            target_hours=goal.target_hours,
            target_date=goal.target_date,
            status="completed",
        )

    elif hours_left > 0 and days_left == 0:
        return GoalResponseSchema(
            topic_id=goal.topic_id,
            target_hours=goal.target_hours,
            target_date=goal.target_date,
            status="overdue",
        )

    current_tempo = hours_done / days_passed if days_passed > 0 else 0
    projected_total_by_deadline = days_left * current_tempo + hours_done
    needed_tempo = 0
    status = "on_track"
    if projected_total_by_deadline < goal.target_hours:
        status = "behind"
        needed_tempo = hours_left / days_left if days_left > 0 else 0

    return GoalResponseSchema(
        topic_id=goal.topic_id,
        target_hours=goal.target_hours,
        target_date=goal.target_date,
        hours_done=hours_done,
        hours_left=hours_left,
        days_left=days_left,
        current_tempo=current_tempo,
        needed_tempo=needed_tempo,
        status=status,
    )

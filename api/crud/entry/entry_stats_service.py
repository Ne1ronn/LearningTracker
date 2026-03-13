from sqlalchemy import select, func
from database.setup import SessionDep
from models import DailyStatsModel, EntryModel, entry_topics, TopicModel, UserModel
from datetime import date, timedelta
from schemas.weekly_stats_schema import WeeklyStatsResponseSchema


async def get_weekly_stats(session: SessionDep, user: UserModel):
    last = date.today() - timedelta(days=6)

    stmt = (
        select(DailyStatsModel.total_hours)
        .where(DailyStatsModel.user_id == user.id, DailyStatsModel.date >= last)
        .order_by(DailyStatsModel.date.asc())
    )
    result = await session.execute(stmt)
    last_7_days_stats = result.scalars().all()

    prev = date.today() - timedelta(days=13)
    stmt = (
        select(DailyStatsModel.total_hours)
        .where(DailyStatsModel.user_id == user.id, DailyStatsModel.date < last, DailyStatsModel.date >= prev)
        .order_by(DailyStatsModel.date.asc())
    )
    result = await session.execute(stmt)
    prev_7_days_stats = result.scalars().all()

    last_7_days_hours = 0
    prev_7_days_hours = 0

    for hours in last_7_days_stats:
        last_7_days_hours += hours
    for hours in prev_7_days_stats:
        prev_7_days_hours += hours

    if not prev_7_days_hours:
        delta_percent = 100
    else:
        delta_percent = 100 * (last_7_days_hours / prev_7_days_hours)

    streak = await count_streak(session, user)

    return WeeklyStatsResponseSchema(
        last_7_days_hours=last_7_days_hours,
        previous_7_days_hours=prev_7_days_hours,
        delta_percent=delta_percent,
        current_streak=streak
    )

async def get_daily_stat(session: SessionDep, user_id: int, entry_date: date):
    stmt = select(DailyStatsModel).where(DailyStatsModel.date == entry_date, DailyStatsModel.user_id == user_id)
    result = await session.execute(stmt)
    daily_stat = result.scalar_one_or_none()

    return daily_stat

async def count_streak(session: SessionDep, user: UserModel):
    stmt = (
        select(DailyStatsModel.date, DailyStatsModel.total_hours)
        .where(DailyStatsModel.user_id == user.id)
        .order_by(DailyStatsModel.date.desc())
    )
    result = await session.execute(stmt)
    daily_stats = result.all()

    streak = 0
    expected_day = date.today()

    for stat_date, hours in daily_stats:
        if stat_date != expected_day:
            break

        if hours <= 0:
            break

        streak += 1
        expected_day -= timedelta(days=1)

    return streak

async def summary(session: SessionDep, user: UserModel):
    stmt = (
        select(
            TopicModel.title,
            func.sum(EntryModel.learning_hours)
        )
        .select_from(TopicModel)
        .join(entry_topics, entry_topics.c.topic_id == TopicModel.id)
        .join(EntryModel, EntryModel.id == entry_topics.c.entry_id)
        .where(EntryModel.user_id == user.id)
        .group_by(TopicModel.id)
    )
    result = await session.execute(stmt)
    rows = result.all()

    data = {}
    for title, hours in rows:
        data[title] = hours

    return data
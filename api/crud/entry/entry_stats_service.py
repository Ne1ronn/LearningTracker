from sqlalchemy import select, func, desc
from database.setup import SessionDep
from models import DailyStatsModel, EntryModel, entry_topics, TopicModel, UserModel
from datetime import date, timedelta
from schemas.profile_stats_schema import ProfileStatsResponseSchema
from schemas.weekly_stats_schema import WeeklyStatsResponseSchema


async def get_profile_stats(session: SessionDep, user: UserModel):
    total_hours_all_time = await get_total_hours_all_time(session, user.id)
    favorite_topic, favorite_topic_hours = await get_favorite_topic(session, user.id)
    current_streak = await count_streak(session, user.id)
    max_streak = await count_max_streak(session, user.id)
    average_day_hours = await get_average_day_hours(session, user.id)

    return ProfileStatsResponseSchema(
        total_hours_all_time=total_hours_all_time,
        average_day_hours=average_day_hours,
        favorite_topic=favorite_topic,
        favorite_topic_hours=favorite_topic_hours,
        current_streak=current_streak,
        max_streak=max_streak,
    )


async def get_total_hours_all_time(session: SessionDep, user_id: int):
    stmt = (
        select(func.sum(DailyStatsModel.total_hours))
        .select_from(DailyStatsModel)
        .where(DailyStatsModel.user_id == user_id)
    )
    result = await session.execute(stmt)
    return result.scalar() or 0.0


async def get_favorite_topic(session: SessionDep, user_id: int):
    stmt = (
        select(
            TopicModel.title, func.sum(EntryModel.learning_hours).label("total_hours")
        )
        .select_from(TopicModel)
        .where(TopicModel.user_id == user_id)
        .join(entry_topics, entry_topics.c.topic_id == TopicModel.id)
        .join(EntryModel, EntryModel.id == entry_topics.c.entry_id)
        .where(EntryModel.user_id == user_id)
        .group_by(TopicModel.id)
        .order_by(desc("total_hours"))
        .limit(1)
    )

    result = await session.execute(stmt)
    favorite_topic_data = result.first()

    favorite_topic = favorite_topic_data[0] if favorite_topic_data else None
    favorite_topic_hours = favorite_topic_data[1] if favorite_topic_data else 0.0

    return favorite_topic, favorite_topic_hours


async def get_average_day_hours(session: SessionDep, user_id: int):
    stmt = (
        select(func.avg(DailyStatsModel.total_hours))
        .select_from(DailyStatsModel)
        .where(DailyStatsModel.user_id == user_id)
    )

    result = await session.execute(stmt)
    return result.scalar() or 0.0


async def get_weekly_stats(session: SessionDep, user: UserModel):
    last = date.today() - timedelta(days=6)

    stmt = select(func.sum(DailyStatsModel.total_hours)).where(
        DailyStatsModel.user_id == user.id, DailyStatsModel.date >= last
    )
    result = await session.execute(stmt)
    last_7_days_hours = result.scalar() or 0.0

    prev = date.today() - timedelta(days=13)
    stmt = select(func.sum(DailyStatsModel.total_hours)).where(
        DailyStatsModel.user_id == user.id,
        DailyStatsModel.date < last,
        DailyStatsModel.date >= prev,
    )
    result = await session.execute(stmt)
    prev_7_days_hours = result.scalar() or 0.0

    if not prev_7_days_hours:
        delta_percent = 100
    else:
        delta_percent = 100 * (last_7_days_hours / prev_7_days_hours)

    streak = await count_streak(session, user.id)

    return WeeklyStatsResponseSchema(
        last_7_days_hours=last_7_days_hours,
        previous_7_days_hours=prev_7_days_hours,
        delta_percent=delta_percent,
        current_streak=streak,
    )


async def get_daily_stat(session: SessionDep, user_id: int, entry_date: date):
    stmt = select(DailyStatsModel).where(
        DailyStatsModel.date == entry_date, DailyStatsModel.user_id == user_id
    )
    result = await session.execute(stmt)
    daily_stat = result.scalar_one_or_none()

    return daily_stat


async def count_streak(session: SessionDep, user_id: int):
    stmt = (
        select(DailyStatsModel.date, DailyStatsModel.total_hours)
        .where(DailyStatsModel.user_id == user_id)
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


async def count_max_streak(session: SessionDep, user_id: int):
    stmt = (
        select(DailyStatsModel.date)
        .where(DailyStatsModel.user_id == user_id, DailyStatsModel.total_hours > 0)
        .order_by(DailyStatsModel.date.asc())
    )
    result = await session.execute(stmt)
    daily_stats = result.scalars().all()

    if not daily_stats:
        return 0

    current_streak = 0
    max_streak = 0
    previous_date = None

    for current_date in daily_stats:
        if previous_date is None:
            current_streak = 1
            previous_date = current_date
            continue

        if current_date == previous_date + timedelta(days=1):
            current_streak += 1
        else:
            if max_streak < current_streak:
                max_streak = current_streak
            current_streak = 1

        previous_date = current_date

    return max_streak if max_streak > current_streak else current_streak


async def summary(session: SessionDep, user: UserModel):
    stmt = (
        select(TopicModel.title, func.sum(EntryModel.learning_hours))
        .select_from(TopicModel)
        .where(TopicModel.user_id == user.id)
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

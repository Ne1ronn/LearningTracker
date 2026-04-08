from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()

import asyncio
import os
from datetime import datetime, UTC, time, timedelta
from zoneinfo import ZoneInfo
from aiogram import Bot
from celery import Celery
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from models import (
    UserModel,
    ReminderLogModel,
    EntryModel,
    TelegramTokenModel,
    QuizModel,
)

app = Celery(
    "celery_app",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
)

DATABASE_URL = os.getenv("DATABASE_URL_ALEMBIC")
BOT_TOKEN = os.getenv("BOT_TOKEN")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

app.conf.beat_schedule = {
    "send_reminder": {
        "task": "celery_app.check_missing_entries_reminders",
        "schedule": 600.0,
    },
    "send_quiz": {
        "task": "celery_app.check_quizzes",
        "schedule": 600.0,
    },
}


@app.task
def check_missing_entries_reminders():
    with SessionLocal() as session:
        stmt = select(UserModel).where(UserModel.reminders_enabled.is_(True))
        result = session.execute(stmt)
        users = result.scalars().all()

        utc_now = datetime.now(UTC)
        for user in users:
            user_timezone = ZoneInfo(user.timezone)
            local_timezone = utc_now.astimezone(user_timezone)

            local_date = local_timezone.date()
            local_time = local_timezone.time()

            if time(21, 0) <= local_time <= time(21, 59):
                local_start = datetime.combine(
                    local_date, time(0, 0), tzinfo=user_timezone
                )
                local_end = local_start + timedelta(days=1)

                utc_start = local_start.astimezone(UTC).replace(tzinfo=None)
                utc_end = local_end.astimezone(UTC).replace(tzinfo=None)
                stmt = select(EntryModel).where(
                    EntryModel.user_id == user.id,
                    EntryModel.created_at >= utc_start,
                    EntryModel.created_at < utc_end,
                )
                result = session.execute(stmt)
                entry = result.scalar()

                if entry is None:
                    stmt = select(ReminderLogModel).where(
                        ReminderLogModel.user_id == user.id,
                        ReminderLogModel.local_date == local_date,
                        ReminderLogModel.reminder_type == "missing_entry",
                    )
                    result = session.execute(stmt)
                    reminder = result.scalar_one_or_none()

                    if reminder is None:
                        stmt = select(TelegramTokenModel.telegram_id).where(
                            TelegramTokenModel.user_id == user.id
                        )
                        result = session.execute(stmt)
                        telegram_id = result.scalar()

                        if telegram_id is not None:
                            asyncio.run(send_missing_entry_reminder(telegram_id))

                            reminder = ReminderLogModel(
                                user_id=user.id,
                                reminder_type="missing_entry",
                                local_date=local_date,
                                sent_at=utc_now.replace(tzinfo=None),
                            )
                            session.add(reminder)

        session.commit()


@app.task
def check_quizzes():
    with SessionLocal() as session:
        stmt = select(UserModel).where(UserModel.reminders_enabled.is_(True))
        result = session.execute(stmt)
        users = result.scalars().all()

        now = datetime.now(UTC)
        for user in users:
            quiz_stmt = (
                select(QuizModel)
                .where(
                    QuizModel.next_review_at <= now,
                    QuizModel.is_active.is_(True),
                    QuizModel.awaiting_response.is_(False),
                )
                .join(EntryModel)
                .where(EntryModel.user_id == user.id)
            )
            quiz_result = session.execute(quiz_stmt)
            quizzes = quiz_result.scalars().all()

            stmt = select(TelegramTokenModel.telegram_id).where(
                TelegramTokenModel.user_id == user.id
            )
            result = session.execute(stmt)
            telegram_id = result.scalar()

            if telegram_id is not None:
                for quiz in quizzes:
                    asyncio.run(send_quiz(telegram_id, quiz.question, quiz.id))
                    quiz.awaiting_response = True

        session.commit()


async def send_missing_entry_reminder(telegram_id: int):
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(
        chat_id=telegram_id,
        text="You still haven't added today's entry",
    )
    await bot.session.close()


async def send_quiz(telegram_id: int, question: str, quiz_id: int):
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(
        chat_id=telegram_id,
        text=(
            "🧠 <b>Time to review the material!</b>\n\n"
            f"❓ <b>Question:</b> {question}\n\n"
            "Choose the button:"
        ),
        reply_markup=create_quiz_buttons(quiz_id),
    )
    await bot.session.close()


def create_quiz_buttons(quiz_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="Show answer", callback_data=f"show_answer:{quiz_id}")
    return builder.as_markup()

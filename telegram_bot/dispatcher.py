from aiogram import Bot, Dispatcher
import asyncio
from telegram_bot.routers.topic_bot.topic_router import router as topic_router
from telegram_bot.routers.entry_bot.entry_router import router as entry_router
from telegram_bot.routers.db_bot.setup_bot import router as db_router
from telegram_bot.routers.auth_bot.auth_router import router as auth_router
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
async def main():
    bot = Bot(token=str(BOT_TOKEN))
    dp = Dispatcher()
    dp.include_router(topic_router)
    dp.include_router(entry_router)
    dp.include_router(auth_router)
    dp.include_router(db_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

from aiogram import Bot, Dispatcher
import asyncio
from telegram_bot.routers.entry_bot.entry_add import router as add_entry_router
from telegram_bot.routers.entry_bot.entry_get import router as get_entry_router
from telegram_bot.routers.db_bot.setup_bot import router as db_router
from telegram_bot.routers.entry_bot.entry_update import router as update_entry_router
from telegram_bot.routers.entry_bot.entry_patch import router as patch_entry_router
from telegram_bot.routers.entry_bot.entry_delete import router as delete_entry_router
from telegram_bot.routers.topic_bot.topic_get import router as topic_get_router
from telegram_bot.routers.topic_bot.topic_add import router as topic_add_router
from telegram_bot.routers.topic_bot.topic_update import router as topic_update_router
from telegram_bot.routers.topic_bot.topic_patch import router as topic_patch_router
from telegram_bot.routers.topic_bot.topic_delete import router as topic_delete_router
from telegram_bot.routers.auth_bot.register import router as auth_router
from telegram_bot.routers.auth_bot.login import router as login_router

async def main():
    bot = Bot(token="8413546619:AAEDhdhZuKjsTCleBs8P5L9QA4_EeNmWtHI")
    dp = Dispatcher()
    dp.include_router(add_entry_router)
    dp.include_router(get_entry_router)
    dp.include_router(update_entry_router)
    dp.include_router(patch_entry_router)
    dp.include_router(delete_entry_router)
    dp.include_router(topic_add_router)
    dp.include_router(topic_get_router)
    dp.include_router(topic_update_router)
    dp.include_router(topic_patch_router)
    dp.include_router(topic_delete_router)
    dp.include_router(auth_router)
    dp.include_router(login_router)
    dp.include_router(db_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

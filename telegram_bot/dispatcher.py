from aiogram import Bot, Dispatcher
import asyncio
from routers.entry_add import router as add_entry_router
from routers.entry_get import router as get_entry_router
from routers.database_bot import router as db_router
from routers.entry_update import router as update_entry_router
from routers.entry_delete import router as delete_entry_router

async def main():
    bot = Bot(token="8413546619:AAEDhdhZuKjsTCleBs8P5L9QA4_EeNmWtHI")
    dp = Dispatcher()
    dp.include_router(add_entry_router)
    dp.include_router(get_entry_router)
    dp.include_router(update_entry_router)
    dp.include_router(delete_entry_router)
    dp.include_router(db_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

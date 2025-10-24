from aiogram import Bot, Dispatcher
import asyncio
from routers.entry_add import router as add_router
from routers.entry_get import router as get_router

async def main():
    bot = Bot(token="8413546619:AAEDhdhZuKjsTCleBs8P5L9QA4_EeNmWtHI")
    dp = Dispatcher()
    dp.include_router(add_router)
    dp.include_router(get_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

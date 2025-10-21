from aiogram import Bot, Dispatcher
import asyncio
from routers.entry_bot import router

async def main():
    bot = Bot(token="8413546619:AAEDhdhZuKjsTCleBs8P5L9QA4_EeNmWtHI")
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

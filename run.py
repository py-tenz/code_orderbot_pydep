import logging
import aiogram
import asyncio
import logging
import asyncio
from aiogram import Dispatcher, Bot
from config import BOT_TOKEN
from app.handlers import router
import dbconnection as db

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


async def main():
    await db.connect()  # Подключение к базе данных
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    asyncio.run(main())
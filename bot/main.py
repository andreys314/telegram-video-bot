import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message


TOKEN = getenv("BOT_TOKEN")

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    bot_username = (await message.bot.me()).username
    await message.answer(f"Привет, Я {bot_username} 🎬")


async def main() -> None:
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is not configured")
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    # Запуск polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

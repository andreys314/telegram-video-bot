import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.use_cases import get_video_info

TOKEN = getenv("BOT_TOKEN")

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    bot_username = (await message.bot.me()).username
    await message.answer(f"Привет, Я {bot_username} 🎬")


@router.message(F.text)
async def youtube_info_handler(message: Message) -> None:
    url = message.text

    if "youtube.com/watch" not in url and "youtu.be/" not in url:
        await message.answer("Отправь ссылку на YouTube 🎬")
        return

    info = await get_video_info(url=message.text)
    if info is None:
        await message.answer("Не удалось получить информацию о видео")
        return

    await message.answer(f'🎬 СМОТРИМ: {info["title"]}\n⏱ Продолжительность: {info["duration"]}')


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

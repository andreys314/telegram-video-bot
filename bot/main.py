import asyncio
import logging
import sys
from os import getenv
from pathlib import Path
from tempfile import TemporaryDirectory

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, FSInputFile, Message

from bot.job_manager import JobManager
from bot.use_cases import (
    download_video,
    get_available_resolutions,
    get_quality_keyboard,
    get_video_info,
)

job_manager = JobManager()

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

    title = info.get("title")
    duration = info.get("duration")
    formats_raw = info.get("formats")

    for fmt in formats_raw:
        if fmt.get("height") == 720:
            print({
                "format_id": fmt.get("format_id"),
                "filesize": fmt.get("filesize"),
                "filesize_approx": fmt.get("filesize_approx"),
                "vcodec": fmt.get("vcodec"),
            })

    resolutions = get_available_resolutions(formats_raw)
    keyboard = get_quality_keyboard(video_id=info.get("id"), resolutions=resolutions)

    await message.answer(
        f"🎬 СМОТРИМ: {title}\n"
        f"⏱ Продолжительность: {duration}\n"
        f"📊 Найдено форматов={len(formats_raw)}",
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("quality:"))
async def quality_handler(callback: CallbackQuery) -> None:
    video_id = callback.data.split(":")[1]
    quality = callback.data.split(":")[2]

    user_id = callback.from_user.id

    if not job_manager.acquire(user_id):
        await callback.answer(
            "У тебя уже есть активная загрузка!",
            show_alert=True,
        )
        return

    await callback.answer()
    await callback.message.answer(f"Выбрано видео: {video_id}, качество: {quality}p 🎬")


    try:
        with TemporaryDirectory() as temp_dir:
            await callback.message.answer("⏳ Начинаю загрузку...")
            path = await download_video(video_id=video_id, resolution=int(quality), output_dir=Path(temp_dir))
            await callback.message.answer("✅ Загрузка завершена!")
            video = FSInputFile(path)
            await callback.message.answer("✅ Загружаю видео в телеграм ...")
            await callback.message.answer_video(video=video, supports_streaming=True)
    except Exception:
        logging.exception("Video download or upload failed")
        await callback.message.answer(
            "❌ Не удалось скачать или отправить видео. Попробуй ещё раз."
        )
    finally:
        job_manager.release(user_id)


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

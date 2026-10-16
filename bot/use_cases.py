import asyncio
import json
from pathlib import Path

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_video_info(url: str) -> dict | None:
    process = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "--dump-single-json",
        "--skip-download",
        url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout_data, _ = await process.communicate()

    if process.returncode == 0:
        return json.loads(stdout_data.decode())

    return None


def format_duration(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    if m >= 60:
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"


def get_available_resolutions(formats: list[dict]) -> list[int]:
    return sorted(
        {
            f.get("height")
            for f in formats
            if f.get("vcodec") not in (None, "none") and f.get("height") is not None
        }
    )


def get_quality_keyboard(video_id: str, resolutions: list[int]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for resolution in resolutions:
        builder.button(
            text=f"🎬 {resolution}p",
            callback_data=f"quality:{video_id}:{resolution}",
        )

    builder.adjust(3)
    return builder.as_markup()


async def download_video(
    video_id: str,
    resolution: int,
    output_dir: Path,
) -> Path:
    url = f"https://www.youtube.com/watch?v={video_id}"

    process = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "--js-runtimes", "node",
        "-f", (
            f"bv[vcodec^=avc1][height={resolution}]"
            "+ba[acodec^=mp4a]"
        ),
        "--merge-output-format", "mp4",
        "-o", str(output_dir / "%(id)s.%(ext)s"),
        url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(
            f"yt-dlp failed: {stderr.decode()}"
        )

    return output_dir / f"{video_id}.mp4"

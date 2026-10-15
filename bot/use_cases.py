import asyncio
import json
import subprocess
import datetime


async def get_video_info(url: str) -> dict | None:
    process = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "--dump-single-json",
        "--skip-download",
        url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout_data, stderr_data = await process.communicate()

    if process.returncode == 0:
        return json.loads(stdout_data.decode())

    return None


def format_duration(seconds: int | float) -> str:
    m, s = divmod(int(seconds), 60)
    if m >= 60:
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"


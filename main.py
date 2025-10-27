import logging
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile
import yt_dlp
import os
from aiohttp import web  # <-- render uchun

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "7900503267:AAGnR8h9GU9G10qny2GZbHdY_49lv9Lfy5E"
ADMIN_ID = 7174828209

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

stats = {"users": set(), "links_count": 0, "daily_users": {}}


def download_video(url):
    ydl_opts = {
        "format": "mp4",
        "outtmpl": "%(title)s.%(ext)s",
        "merge_output_format": "mp4",
        "nonplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    caption = "🎬 Salom! Menga YouTube, TikTok yoki Instagram link yuboring — men sizga videoni yuklab beraman 🎥"
    await message.answer(caption)


@dp.message(F.text)
async def link_handler(message: types.Message):
    url = message.text.strip()
    if not url.startswith("http"):
        await message.answer("🚫 Bu havola emas, iltimos haqiqiy link yuboring.")
        return

    stats["users"].add(message.from_user.id)
    stats["links_count"] += 1
    stats["daily_users"][message.from_user.id] = datetime.now().date()

    await message.answer("⏳ Video yuklanmoqda, biroz kuting…")

    try:
        filename = await asyncio.to_thread(download_video, url)
        video = FSInputFile(filename)
        await message.answer_video(video)
    except Exception as e:
        await message.answer(f"⚠️ Xatolik: video yuklanmadi.\n{e}")


async def run_bot():
    await dp.start_polling(bot)


# 🔹 Render uchun soxta web-server (port ochish)
async def handle(request):
    return web.Response(text="Bot is running!")

async def main():
    app = web.Application()
    app.add_routes([web.get("/", handle)])
    asyncio.create_task(run_bot())  # Bot pollingi parallel ishlaydi

    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
import yt_dlp
from datetime import datetime

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "7900503267:AAGnR8h9GU9G10qny2GZbHdY_49lv9Lfy5E"
ADMIN_ID = 7174828209

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

stats = {
    "users": set(),
    "links_count": 0,
    "daily_users": {}
}

def download_video(url):
    ydl_opts = {
        "format": "mp4",
        "outtmpl": "%(title)s.%(ext)s",
        "merge_output_format": "mp4",
        "nonplaylist": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

@dp.message(Command("start"))
async def start_handler(message: Message):
    photo_path = "qoshiq.png"
    caption = "Привет! Отправьте мне ссылку на YouTube/TikTok/Instagram, и я сделаю для вас видео."
    with open(photo_path, "rb") as photo:
        await message.answer_photo(photo, caption=caption)

@dp.message(Command("statistics1bot"))
async def stats_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Siz admin emassiz!")
        return

    today = datetime.now().date()
    daily_active = sum(1 for d in stats["daily_users"].values() if d == today)
    await message.answer(
        f"📊 Statistika:\n\n"
        f"✅ Foydalanuvchilar: {len(stats['users'])}\n"
        f"🔗 Linklar soni: {stats['links_count']}\n"
        f"📅 Kunlik aktiv foydalanuvchilar: {daily_active}"
    )

@dp.message()
async def link_handler(message: Message):
    url = message.text.strip()
    if not url.startswith("http"):
        await message.answer("Это не ссылка, пожалуйста, отправьте ссылку.")
        return

    stats["users"].add(message.from_user.id)
    stats["links_count"] += 1
    stats["daily_users"][message.from_user.id] = datetime.now().date()

    await message.answer("Идёт загрузка, подождите немного…")

    try:
        filename = download_video(url)
        with open(filename, "rb") as video:
            await message.answer_video(video)
    except Exception as e:
        await message.answer(f"Ошибка: видео не загружено. {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

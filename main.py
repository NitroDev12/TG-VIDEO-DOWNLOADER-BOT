import logging
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile
import yt_dlp

# 📋 Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# 🔑 Token va admin ID
BOT_TOKEN = "7900503267:AAGnR8h9GU9G10qny2GZbHdY_49lv9Lfy5E"
ADMIN_ID = 7174828209

# 🧠 Bot sozlamalari (parse_mode endi shu tarzda beriladi)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# 📊 Statistika uchun oddiy xotira
stats = {
    "users": set(),
    "links_count": 0,
    "daily_users": {}
}


def download_video(url: str):
    ydl_opts = {
        "format": "mp4",
        "outtmpl": "%(title)s.%(ext)s",
        "merge_output_format": "mp4",
        "nonplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "cookies": "cookies.txt", 
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# 🏁 /start komandasi
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    photo_path = "qoshiq.png"
    caption = (
        "🎬 <b>Salom!</b>\n\n"
        "Menga <b>YouTube</b>, <b>TikTok</b> yoki <b>Instagram</b> link yuboring — "
        "men sizga videoni yuklab beraman 🎥"
    )
    try:
        await message.answer_photo(FSInputFile(photo_path), caption=caption)
    except Exception:
        await message.answer(caption)  # Agar rasm topilmasa, faqat matn yuboriladi


# 📈 /statistics1bot komandasi (faqat admin uchun)
@dp.message(Command("statistics1bot"))
async def stats_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 Siz admin emassiz!")
        return

    today = datetime.now().date()
    daily_active = sum(1 for d in stats["daily_users"].values() if d == today)
    await message.answer(
        f"📊 <b>Statistika:</b>\n\n"
        f"👤 Foydalanuvchilar: <b>{len(stats['users'])}</b>\n"
        f"🔗 Yuklangan linklar: <b>{stats['links_count']}</b>\n"
        f"📅 Bugungi aktivlar: <b>{daily_active}</b>"
    )


# 🔗 Foydalanuvchi link yuborganda
@dp.message(F.text)
async def link_handler(message: types.Message):
    url = message.text.strip()
    if not url.startswith("http"):
        await message.answer("🚫 Bu havola emas, iltimos haqiqiy link yuboring.")
        return

    # Statistikani yangilash
    stats["users"].add(message.from_user.id)
    stats["links_count"] += 1
    stats["daily_users"][message.from_user.id] = datetime.now().date()

    await message.answer("⏳ Video yuklanmoqda, biroz kuting…")

    try:
        filename = await asyncio.to_thread(download_video, url)  # ⚡ yuklashni async fon rejimda
        video = FSInputFile(filename)
        await message.answer_video(video)
    except Exception as e:
        logging.error(f"Video yuklashda xatolik: {e}")
        await message.answer(f"⚠️ Xatolik: video yuklanmadi.\n<code>{e}</code>")


# 🚀 Botni ishga tushirish
async def main():
    logging.info("Bot ishga tushdi ✅")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

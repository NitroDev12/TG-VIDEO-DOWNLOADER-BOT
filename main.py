import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import Message
import yt_dlp

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "7900503267:AAGnR8h9GU9G10qny2GZbHdY_49lv9Lfy5E"
ADMIN_ID = 7174828209  # <-- bu yerga o'zingizning ID'ingizni yozing

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# /start komandasi
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    photo_path = "qoshiq.png"
    caption = "Привет! Отправьте мне ссылку на YouTube/TikTok/Instagram, и я сделаю для вас видео."
    with open(photo_path, "rb") as photo:
        await message.answer_photo(photo=photo, caption=caption)

# Video yuklash funksiyasi
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

# Linklarni qabul qiluvchi handler
from datetime import datetime, timedelta

# Statistika uchun dictionary
stats = {
    "users": set(),          # Umumiy unikal foydalanuvchilar
    "links_count": 0,        # Umumiy linklar soni
    "daily_users": {}        # {user_id: last_active_date}
}

# /stats komandasi faqat admin uchun
@dp.message_handler(commands=["statistics1bot"])
async def stats_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Siz admin emassiz!")
        return

    # Hozirgi kun
    today = datetime.now().date()
    # Kunlik aktiv foydalanuvchilar
    daily_active = sum(1 for date in stats["daily_users"].values() if date == today)

    total_users = len(stats["users"])
    total_links = stats["links_count"]

    await message.answer(
        f"📊 Statistika:\n\n"
        f"✅ Foydalanuvchilar: {total_users}\n"
        f"🔗 Linklar soni: {total_links}\n"
        f"📅 Kunlik aktiv foydalanuvchilar: {daily_active}"
    )

# Linklarni qabul qiluvchi handler
@dp.message_handler()
async def link_handler(message: types.Message):
    url = message.text.strip()
    if not url.startswith("http"):
        await message.answer("Это не ссылка, пожалуйста, отправьте ссылку.")
        return

    # Statistika yangilash
    stats["users"].add(message.from_user.id)
    stats["links_count"] += 1
    stats["daily_users"][message.from_user.id] = datetime.now().date()  # so‘nggi faoliyat sanasi

    await message.answer("Идёт загрузка, подождите немного…")

    try:
        filename = download_video(url)
        with open(filename, "rb") as video:
            await bot.send_video(chat_id=message.chat.id, video=video)
    except Exception as e:
        await message.answer(f"Ошибка: видео не загружено. {e}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

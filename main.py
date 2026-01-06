import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from keep_alive import keep_alive  # pastikan keep_alive.py ada

# ================= CONFIG =================
TOKEN = os.environ.get("BOT_TOKEN") or "YOUR_BOT_TOKEN"
CHANNEL = "@datsfilm"
ADS_LINK = "https://furtivelywhipped.com/q00qna4eu?key=92c3ecbcc3001e57f320e444bce7b52f"
ADMIN_ID = int(os.environ.get("ADMIN_ID") or 8246649852)
DATA_FILE = "files.json"
# =========================================

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ================= DATA ====================
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        FILES = json.load(f)
else:
    FILES = {}

USER_STEP = {}  # user_id -> "ADS" / "CODE"


def save_files():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(FILES, f, ensure_ascii=False, indent=4)


# ================= START ==================
@dp.message(Command("start"))
async def start(msg: types.Message):
    USER_STEP[msg.from_user.id] = "ADS"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="JOIN CHANNEL", url=f"https://t.me/{CHANNEL.strip('@')}")],
        [InlineKeyboardButton(text="KLIK IKLAN", url=ADS_LINK)],
        [InlineKeyboardButton(text="✅ SAYA SUDAH KLIK", callback_data="ads_ok")]
    ])
    await msg.answer(
        "🎬 *Selamat datang di DatsFilmBot!*\n\n"
        "Sebelum lanjut, kamu harus join channel resmi kami dulu ya 👇\n\n"
        "Silahkan klik tombol iklan di bawah dan wajib buka/open iklan sampai terbuka, "
        "kemudian tekan tombol ✅ *Saya sudah klik* untuk melanjutkan.",
        parse_mode="Markdown",
        reply_markup=kb
    )


# ================= ADS OK ==================
@dp.callback_query(lambda c: c.data == "ads_ok")
async def ads_ok(call: types.CallbackQuery):
    USER_STEP[call.from_user.id] = "CODE"
    await call.message.answer("Masukkan CODE film untuk mendapatkan link dan gambar 🎬")
    await call.answer()  # hilangkan loading


# ================= ADD FILE (ADMIN) =========
@dp.message(lambda m: m.photo and m.caption and m.caption.startswith("/add"))
async def add_file_photo(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    try:
        _, code, link = msg.caption.split(maxsplit=2)
        photo_id = msg.photo[-1].file_id
        FILES[code.upper()] = {"img": photo_id, "link": link.strip()}
        save_files()
        await msg.answer("✅ CODE + GAMBAR BERHASIL DITAMBAHKAN")
    except ValueError:
        await msg.answer(
            "FORMAT SALAH\n\nKIRIM FOTO + CAPTION:\n/add CODE LINK"
        )


# ================= GET FILE ==================
@dp.message(lambda m: True)
async def get_file(msg: types.Message):
    uid = msg.from_user.id
    code = msg.text.strip().upper()

    if USER_STEP.get(uid) != "CODE":
        return

    if code not in FILES:
        await msg.answer("❌ CODE TIDAK DITEMUKAN")
        return

    data = FILES[code]
    caption = f"🎬 Selamat menonton\n\n{data['link']}"
    await bot.send_photo(uid, data["img"], caption=caption)


# ================= RUN BOT ==================
async def main():
    keep_alive()  # agar terus jalan di Choreo/Replit
    print("🚀 Bot sedang berjalan...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

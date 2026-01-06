import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask
from threading import Thread

# ================= CONFIG =================
TOKEN = "8204617808:AAG4ERyX7tgGJoggiow00y9_ppwdxH0LL5o"
CHANNEL = "@datsfilm"
ADS_LINK = "https://furtivelywhipped.com/q00qna4eu?key=92c3ecbcc3001e57f320e444bce7b52f"
ADMIN_ID = 8246649852
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

USER_STEP = {}


def save_files():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(FILES, f, ensure_ascii=False, indent=4)


# ================= KEEP ALIVE =================
app = Flask("")

@app.route("/")
def home():
    return "Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=8081)

def keep_alive():
    Thread(target=run, daemon=True).start()


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
        "Silakan join channel & klik iklan untuk lanjut.",
        parse_mode="Markdown",
        reply_markup=kb
    )


@dp.callback_query(lambda c: c.data == "ads_ok")
async def ads_ok(call: types.CallbackQuery):
    USER_STEP[call.from_user.id] = "CODE"
    await call.message.answer("Masukkan CODE film 🎬")


@dp.message(lambda m: m.photo is not None)
async def add_file_photo(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    if not msg.caption or not msg.caption.startswith("/add"):
        await msg.answer("FORMAT:\n/add CODE LINK")
        return

    try:
        _, code, link = msg.caption.split(maxsplit=2)
        FILES[code.upper()] = {
            "img": msg.photo[-1].file_id,
            "link": link
        }
        save_files()
        await msg.answer("✅ BERHASIL DITAMBAHKAN")
    except:
        await msg.answer("FORMAT SALAH")


@dp.message()
async def get_file(msg: types.Message):
    if USER_STEP.get(msg.from_user.id) != "CODE":
        return

    code = msg.text.upper()
    if code not in FILES:
        await msg.answer("❌ CODE TIDAK DITEMUKAN")
        return

    data = FILES[code]
    await bot.send_photo(msg.from_user.id, data["img"], caption=data["link"])


async def main():
    keep_alive()
    print("🚀 Bot running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

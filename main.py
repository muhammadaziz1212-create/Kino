import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, ADMIN_IDS
from database import *

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# ── STATES ──
class AddMovie(StatesGroup):
    code = State()
    title = State()
    desc = State()
    video = State()

class DelMovie(StatesGroup):
    query = State()

class Broadcast(StatesGroup):
    msg = State()

# ── KEYBOARDS ──
def admin_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🎬 Kino qo'shish", callback_data="add"),
        InlineKeyboardButton("🗑 Kino o'chirish", callback_data="delete"),
        InlineKeyboardButton("📊 Statistika", callback_data="stats"),
        InlineKeyboardButton("📢 Xabar yuborish", callback_data="broadcast"),
        InlineKeyboardButton("🎥 Kinolar ro'yxati", callback_data="list")
    )
    return kb

def cancel_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel"))
    return kb

def back_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back"))
    return kb

def is_admin(uid):
    return uid in ADMIN_IDS

# ── USER HANDLERS ──
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    u = message.from_user
    register_user(u.id, u.username or "", u.full_name or "")
    total = get_total_users()
    await message.answer(
        f"🎬 <b>Spekter Kino Botiga xush kelibsiz!</b>\n\n"
        f"🔍 Kino topish uchun kod yoki nom yuboring\n"
        f"💡 Masalan: <code>001</code>\n\n"
        f"👥 Foydalanuvchilar: <b>{total}</b> ta",
        parse_mode="HTML"
    )

@dp.message_handler(commands=["admin"])
async def admin_panel(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("❌ Ruxsat yo'q!")
    await message.answer(
        f"👑 <b>ADMIN PANEL</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"👥 Foydalanuvchilar: <b>{get_total_users()}</b>\n"
        f"🎬 Kinolar: <b>{get_movies_count()}</b>\n"
        f"━━━━━━━━━━━━━",
        reply_markup=admin_kb(), parse_mode="HTML"
    )

@dp.message_handler(content_types=types.ContentType.TEXT)
async def search(message: types.Message):
    u = message.from_user
    register_user(u.id, u.username or "", u.full_name or "")
    q = message.text.strip()
    movie = get_movie(q)
    if movie:
        return await send_movie(message, movie)
    results = search_movie(q)
    if len(results) == 1:
        return await send_movie(message, results[0])
    elif len(results) > 1:
        text = "🔍 <b>Bir nechta kino topildi:</b>\n\n"
        for m in results[:5]:
            text += f"🎬 <b>{m['title']}</b> — <code>{m['code']}</code>\n"
        await message.answer(text + "\n💡 Kino kodini yuboring", parse_mode="HTML")
    else:
        await message.answer("❌ <b>Kino topilmadi!</b>\n\nKod yoki nom to'g'ri kiriting", parse_mode="HTML")

async def send_movie(message, movie):
    cap = f"🎬 <b>{movie['title']}</b>\n🔑 Kod: <code>{movie['code']}</code>"
    if movie.get("description"):
        cap += f"\n📝 {movie['description']}"
    try:
        await bot.send_video(message.chat.id, movie["file_id"], caption=cap, parse_mode="HTML")
    except:
        try:
            await bot.send_document(message.chat.id, movie["file_id"], caption=cap, parse_mode="HTML")
        except:
            await message.answer(cap, parse_mode="HTML")

# ── ADMIN CALLBACKS ──
@dp.callback_query_handler(lambda c: c.data == "stats")
async def cb_stats(call: types.CallbackQuery):
    if not is_admin(call.from_user.id): return
    await call.message.edit_text(
        f"📊 <b>STATISTIKA</b>\n━━━━━━━━━━━━━\n"
        f"👥 Foydalanuvchilar: <b>{get_total_users()}</b>\n"
        f"🎬 Kinolar: <b>{get_movies_count()}</b>",
        reply_markup=back_kb(), parse_mode="HTML"
    )

@dp.callback_query_handler(lambda c: c.data == "list")
async def cb_list(call: types.CallbackQuery):
    if not is_admin(call.from_user.id): return
    movies = load_movies()
    if not movies:
        text = "🎬 Hozircha kino yo'q!"
    else:
        text = f"🎥 <b>KINOLAR</b> ({len(movies)} ta)\n━━━━━━━━━━━━━\n"
        for code, m in list(movies.items())[:20]:
            text += f"• <code>{code}</code> — {m['title']}\n"
    await call.message.edit_text(text, reply_markup=back_kb(), parse_mode="HTML")

@dp.callback_query_handler(lambda c: c.data == "back")
async def cb_back(call: types.CallbackQuery):
    if not is_admin(call.from_user.id): return
    await call.message.edit_text(
        f"👑 <b>ADMIN PANEL</b>\n━━━━━━━━━━━━━\n"
        f"👥 Foydalanuvchilar: <b>{get_total_users()}</b>\n"
        f"🎬 Kinolar: <b>{get_movies_count()}</b>",
        reply_markup=admin_kb(), parse_mode="HTML"
    )

@dp.callback_query_handler(lambda c: c.data == "cancel", state="*")
async def cb_cancel(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text(
        f"👑 <b>ADMIN PANEL</b>\n━━━━━━━━━━━━━\n"
        f"👥 Foydalanuvchilar: <b>{get_total_users()}</b>\n"
        f"🎬 Kinolar: <b>{get_movies_count()}</b>",
        reply_markup=admin_kb(), parse_mode="HTML"
    )

# ── ADD MOVIE ──
@dp.callback_query_handler(lambda c: c.data == "add")
async def cb_add(call: types.CallbackQuery):
    if not is_admin(call.from_user.id): return
    await AddMovie.code.set()
    await call.message.edit_text("🎬 <b>Kino kodi:</b>\n💡 Masalan: <code>001</code>", reply_markup=cancel_kb(), parse_mode="HTML")

@dp.message_handler(state=AddMovie.code)
async def add_code(message: types.Message, state: FSMContext):
    await state.update_data(code=message.text.strip().upper())
    await AddMovie.title.set()
    await message.answer(f"✅ Kod: <code>{message.text.upper()}</code>\n\n📝 <b>Kino nomi:</b>", parse_mode="HTML")

@dp.message_handler(state=AddMovie.title)
async def add_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await AddMovie.desc.set()
    await message.answer("📋 <b>Tavsif yozing</b>\n(O'tkazib yuborish: <code>-</code>)", parse_mode="HTML")

@dp.message_handler(state=AddMovie.desc)
async def add_desc(message: types.Message, state: FSMContext):
    desc = "" if message.text.strip() == "-" else message.text.strip()
    await state.update_data(desc=desc)
    await AddMovie.video.set()
    await message.answer("🎬 <b>Kino faylini yuboring</b>", parse_mode="HTML")

@dp.message_handler(state=AddMovie.video, content_types=[types.ContentType.VIDEO, types.ContentType.DOCUMENT])
async def add_video(message: types.Message, state: FSMContext):
    file_id = message.video.file_id if message.video else message.document.file_id
    data = await state.get_data()
    add_movie(data["code"], data["title"], file_id, data.get("desc", ""))
    await state.finish()
    await message.answer(f"✅ <b>Kino qo'shildi!</b>\n🔑 Kod: <code>{data['code']}</code>\n🎬 Nom: <b>{data['title']}</b>", parse_mode="HTML")

# ── DELETE MOVIE ──
@dp.callback_query_handler(lambda c: c.data == "delete")
async def cb_delete(call: types.CallbackQuery):
    if not is_admin(call.from_user.id): return
    await DelMovie.query.set()
    await call.message.edit_text("🗑 <b>Kino o'chirish</b>\n\nKod yoki nom yuboring:", reply_markup=cancel_kb(), parse_mode="HTML")

@dp.message_handler(state=DelMovie.query)
async def do_delete(message: types.Message, state: FSMContext):
    success = delete_movie(message.text.strip())
    await state.finish()
    if success:
        await message.answer(f"✅ <b>O'chirildi!</b> «{message.text}»", parse_mode="HTML")
    else:
        await message.answer(f"❌ <b>Topilmadi!</b> «{message.text}»", parse_mode="HTML")

# ── BROADCAST ──
@dp.callback_query_handler(lambda c: c.data == "broadcast")
async def cb_broadcast(call: types.CallbackQuery):
    if not is_admin(call.from_user.id): return
    await Broadcast.msg.set()
    await call.message.edit_text(
        f"📢 <b>XABAR YUBORISH</b>\n👥 {get_total_users()} ta obunachi\n\nXabar yuboring:",
        reply_markup=cancel_kb(), parse_mode="HTML"
    )

@dp.message_handler(state=Broadcast.msg, content_types=types.ContentType.ANY)
async def do_broadcast(message: types.Message, state: FSMContext):
    await state.finish()
    ids = get_all_user_ids()
    sent = failed = 0
    await message.answer(f"📤 Yuborilmoqda... ({len(ids)} ta)")
    for uid in ids:
        try:
            await message.copy_to(uid)
            sent += 1
        except:
            failed += 1
    await message.answer(f"✅ <b>Tayyor!</b>\n✔️ Yuborildi: <b>{sent}</b>\n❌ Xato: <b>{failed}</b>", parse_mode="HTML")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

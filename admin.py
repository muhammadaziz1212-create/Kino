from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS
from database import (
    add_movie, delete_movie, get_movies_count,
    get_total_users, get_all_user_ids, load_movies
)

router = Router()

# ───── STATES ─────
class AddMovie(StatesGroup):
    waiting_code = State()
    waiting_title = State()
    waiting_description = State()
    waiting_video = State()

class DeleteMovie(StatesGroup):
    waiting_query = State()

class Broadcast(StatesGroup):
    waiting_message = State()

# ───── ADMIN CHECK ─────
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# ───── ADMIN PANEL ─────
def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 Kino qo'shish", callback_data="add_movie"),
            InlineKeyboardButton(text="🗑 Kino o'chirish", callback_data="delete_movie")
        ],
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="stats"),
            InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="broadcast")
        ],
        [
            InlineKeyboardButton(text="🎥 Kinolar ro'yxati", callback_data="movie_list")
        ]
    ])

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return await message.answer("❌ Sizda ruxsat yo'q!")
    
    total_users = get_total_users()
    total_movies = get_movies_count()
    
    text = (
        f"👑 <b>ADMIN PANEL</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👥 Foydalanuvchilar: <b>{total_users}</b>\n"
        f"🎬 Kinolar soni: <b>{total_movies}</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Quyidagi tugmalardan birini tanlang:"
    )
    await message.answer(text, reply_markup=admin_keyboard(), parse_mode="HTML")

# ───── STATISTIKA ─────
@router.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    
    total_users = get_total_users()
    total_movies = get_movies_count()
    
    text = (
        f"📊 <b>STATISTIKA</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
        f"🎬 Jami kinolar: <b>{total_movies}</b>\n"
        f"━━━━━━━━━━━━━━━"
    )
    back_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_admin")]
    ])
    await callback.message.edit_text(text, reply_markup=back_btn, parse_mode="HTML")

# ───── KINOLAR RO'YXATI ─────
@router.callback_query(F.data == "movie_list")
async def show_movie_list(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    
    movies = load_movies()
    if not movies:
        text = "🎬 Hozircha kinolar yo'q!"
    else:
        text = f"🎥 <b>KINOLAR RO'YXATI</b> ({len(movies)} ta)\n━━━━━━━━━━━━━━━\n"
        for code, movie in list(movies.items())[:20]:
            text += f"• <code>{code}</code> — {movie['title']}\n"
        if len(movies) > 20:
            text += f"\n... va yana {len(movies)-20} ta kino"
    
    back_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_admin")]
    ])
    await callback.message.edit_text(text, reply_markup=back_btn, parse_mode="HTML")

# ───── KINO QO'SHISH ─────
@router.callback_query(F.data == "add_movie")
async def start_add_movie(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AddMovie.waiting_code)
    cancel_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])
    await callback.message.edit_text(
        "🎬 <b>KINO QO'SHISH</b>\n\n"
        "1️⃣ Kino kodini yuboring:\n"
        "💡 Masalan: <code>001</code>, <code>A001</code>",
        reply_markup=cancel_btn,
        parse_mode="HTML"
    )

@router.message(AddMovie.waiting_code)
async def get_movie_code(message: Message, state: FSMContext):
    code = message.text.strip().upper()
    await state.update_data(code=code)
    await state.set_state(AddMovie.waiting_title)
    await message.answer(
        f"✅ Kod: <code>{code}</code>\n\n"
        f"2️⃣ Kino nomini yuboring:",
        parse_mode="HTML"
    )

@router.message(AddMovie.waiting_title)
async def get_movie_title(message: Message, state: FSMContext):
    title = message.text.strip()
    await state.update_data(title=title)
    await state.set_state(AddMovie.waiting_description)
    await message.answer(
        f"✅ Nom: <b>{title}</b>\n\n"
        f"3️⃣ Qisqacha tavsif yuboring:\n"
        f"(O'tkazib yuborish uchun <code>-</code> yuboring)",
        parse_mode="HTML"
    )

@router.message(AddMovie.waiting_description)
async def get_movie_description(message: Message, state: FSMContext):
    desc = "" if message.text.strip() == "-" else message.text.strip()
    await state.update_data(description=desc)
    await state.set_state(AddMovie.waiting_video)
    await message.answer(
        "4️⃣ <b>Kino faylini yuboring</b> 🎬\n\n"
        "📌 Video yoki hujjat sifatida yuborishingiz mumkin",
        parse_mode="HTML"
    )

@router.message(AddMovie.waiting_video, F.video | F.document)
async def get_movie_video(message: Message, state: FSMContext):
    if message.video:
        file_id = message.video.file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        return await message.answer("❌ Iltimos video yuboring!")
    
    data = await state.get_data()
    add_movie(data["code"], data["title"], file_id, data.get("description", ""))
    await state.clear()
    
    await message.answer(
        f"✅ <b>Kino muvaffaqiyatli qo'shildi!</b>\n\n"
        f"🔑 Kod: <code>{data['code']}</code>\n"
        f"🎬 Nom: <b>{data['title']}</b>\n\n"
        f"👤 Foydalanuvchilar endi bu kinoni kod orqali topa oladi!",
        parse_mode="HTML"
    )

# ───── KINO O'CHIRISH ─────
@router.callback_query(F.data == "delete_movie")
async def start_delete_movie(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(DeleteMovie.waiting_query)
    cancel_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])
    await callback.message.edit_text(
        "🗑 <b>KINO O'CHIRISH</b>\n\n"
        "Kinoni o'chirish uchun:\n"
        "• Kino <b>kodini</b> yuboring (masalan: <code>001</code>)\n"
        "• Yoki kino <b>nomini</b> yuboring",
        reply_markup=cancel_btn,
        parse_mode="HTML"
    )

@router.message(DeleteMovie.waiting_query)
async def process_delete(message: Message, state: FSMContext):
    query = message.text.strip()
    success = delete_movie(query)
    await state.clear()
    
    if success:
        await message.answer(
            f"✅ <b>Kino o'chirildi!</b>\n"
            f"🗑 «{query}» bazadan o'chirildi.",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            f"❌ <b>Kino topilmadi!</b>\n\n"
            f"«{query}» kod yoki nomli kino bazada yo'q.\n"
            f"Kinolar ro'yxatini ko'rish uchun /admin → Kinolar ro'yxati",
            parse_mode="HTML"
        )

# ───── XABAR YUBORISH ─────
@router.callback_query(F.data == "broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(Broadcast.waiting_message)
    cancel_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])
    total = get_total_users()
    await callback.message.edit_text(
        f"📢 <b>XABAR YUBORISH</b>\n\n"
        f"👥 Obunachilarga yuboriladi: <b>{total}</b> ta\n\n"
        f"Xabar matnini yuboring:\n"
        f"(Rasm, video yoki matn bo'lishi mumkin)",
        reply_markup=cancel_btn,
        parse_mode="HTML"
    )

@router.message(Broadcast.waiting_message)
async def send_broadcast(message: Message, state: FSMContext):
    await state.clear()
    user_ids = get_all_user_ids()
    
    sent = 0
    failed = 0
    
    await message.answer(f"📤 Xabar yuborilmoqda... ({len(user_ids)} ta foydalanuvchi)")
    
    for user_id in user_ids:
        try:
            if message.text:
                await message.bot.send_message(user_id, message.text)
            elif message.photo:
                await message.bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption or "")
            elif message.video:
                await message.bot.send_video(user_id, message.video.file_id, caption=message.caption or "")
            elif message.document:
                await message.bot.send_document(user_id, message.document.file_id, caption=message.caption or "")
            sent += 1
        except Exception:
            failed += 1
    
    await message.answer(
        f"✅ <b>Xabar yuborildi!</b>\n\n"
        f"✔️ Muvaffaqiyatli: <b>{sent}</b>\n"
        f"❌ Yuborilmadi: <b>{failed}</b>",
        parse_mode="HTML"
    )

# ───── ORQAGA / BEKOR QILISH ─────
@router.callback_query(F.data == "back_admin")
async def back_to_admin(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    total_users = get_total_users()
    total_movies = get_movies_count()
    text = (
        f"👑 <b>ADMIN PANEL</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👥 Foydalanuvchilar: <b>{total_users}</b>\n"
        f"🎬 Kinolar soni: <b>{total_movies}</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Quyidagi tugmalardan birini tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=admin_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await back_to_admin(callback)

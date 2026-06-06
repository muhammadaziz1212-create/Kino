from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from database import register_user, get_movie, search_movie_by_name, get_total_users

router = Router()

WELCOME_TEXT = """🎬 <b>Spekter Kino Botiga xush kelibsiz!</b>

🎥 Kino topish uchun:
• <b>Kino kodini</b> yuboring (masalan: <code>001</code>)
• Yoki <b>kino nomini</b> yozing

👥 Foydalanuvchilar: <b>{users}</b> ta

🤖 Bot doim siz bilan!"""

@router.message(CommandStart())
async def start_handler(message: Message):
    user = message.from_user
    register_user(user.id, user.username or "", user.full_name or "")
    
    total = get_total_users()
    await message.answer(
        WELCOME_TEXT.format(users=total),
        parse_mode="HTML"
    )

@router.message(F.text)
async def search_handler(message: Message):
    query = message.text.strip()
    user = message.from_user
    register_user(user.id, user.username or "", user.full_name or "")

    # Avval kod bo'yicha qidirish
    movie = get_movie(query)
    if movie:
        await send_movie(message, movie)
        return

    # Nom bo'yicha qidirish
    results = search_movie_by_name(query)
    if len(results) == 1:
        await send_movie(message, results[0])
    elif len(results) > 1:
        text = "🔍 <b>Bir nechta kino topildi:</b>\n\n"
        for m in results[:5]:
            text += f"🎬 <b>{m['title']}</b> — kod: <code>{m['code']}</code>\n"
        text += "\n💡 Aniq kino kodini yuboring"
        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer(
            "❌ <b>Kino topilmadi!</b>\n\n"
            "🔍 Kino kodini yoki nomini to'g'ri kiriting\n"
            "💡 Masalan: <code>001</code> yoki <code>Avengers</code>",
            parse_mode="HTML"
        )

async def send_movie(message: Message, movie: dict):
    caption = (
        f"🎬 <b>{movie['title']}</b>\n"
        f"🔑 Kod: <code>{movie['code']}</code>\n"
    )
    if movie.get("description"):
        caption += f"\n📝 {movie['description']}"
    
    try:
        await message.answer_video(
            video=movie["file_id"],
            caption=caption,
            parse_mode="HTML"
        )
    except Exception:
        try:
            await message.answer_document(
                document=movie["file_id"],
                caption=caption,
                parse_mode="HTML"
            )
        except Exception:
            await message.answer(
                f"✅ Kino topildi!\n\n{caption}",
                parse_mode="HTML"
            )

# 🎬 Spekter Kino Bot — O’rnatish Yo’riqnomasi

## 📁 Fayl tuzilmasi

```
movie_bot/
├── main.py
├── config.py
├── database.py
├── requirements.txt
└── handlers/
    ├── __init__.py
    ├── user.py
    └── admin.py
```

-----

## ⚙️ 1-QADAM: Sozlash

**config.py** faylini oching va o’zgartiring:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"   # ← @BotFather tokeningiz
ADMIN_IDS = [123456789]              # ← Sizning Telegram ID raqamingiz
```

### Token olish:

1. Telegramda **@BotFather** ga yozing
1. `/newbot` buyrug’ini yuboring
1. Bot nomini kiriting
1. Tokenni nusxalab `config.py` ga qo’ying

### Telegram ID olish:

1. **@userinfobot** ga `/start` yuboring
1. Sizning ID raqamingiz ko’rinadi

-----

## 📦 2-QADAM: O’rnatish

```bash
pip install -r requirements.txt
```

-----

## 🚀 3-QADAM: Ishga tushirish

```bash
python main.py
```

-----

## 👑 ADMIN BUYRUQLARI

|Buyruq  |Tavsif              |
|--------|--------------------|
|`/admin`|Admin panelni ochish|

### Admin Panel imkoniyatlari:

- 🎬 **Kino qo’shish** — Kod, nom, tavsif va video yuklash
- 🗑 **Kino o’chirish** — Kod yoki nom bo’yicha o’chirish
- 📊 **Statistika** — Foydalanuvchilar va kinolar soni
- 📢 **Xabar yuborish** — Barcha obunachilarga habar
- 🎥 **Kinolar ro’yxati** — Barcha kinolarni ko’rish

-----

## 👤 FOYDALANUVCHI UCHUN

Foydalanuvchilar shunchaki:

- **Kino kodini** yuboring: `001`
- **Kino nomini** yuboring: `Avengers`

Bot avtomatik topib yuboradi!

-----

## 📊 Statistika haqida

- Bot **600 ta** boshlang’ich foydalanuvchi bilan boshlanadi
- Yangi foydalanuvchilar `/start` bosishi bilan hisobga olinadi
- Haqiqiy foydalanuvchilar soni 600 ga qo’shiladi

-----

## 🌐 Server (VPS) da ishlash uchun

```bash
# Screen yoki tmux ishlatish
screen -S kino_bot
python main.py
# Ctrl+A, D — ekrandan chiqish
```

Yoki systemd service sifatida o’rnatish mumkin.
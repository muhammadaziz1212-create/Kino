import json
import os
from config import INITIAL_USERS

MOVIES_FILE = "movies.json"
USERS_FILE = "users.json"

# ───── MOVIES ─────

def load_movies() -> dict:
    if os.path.exists(MOVIES_FILE):
        with open(MOVIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_movies(data: dict):
    with open(MOVIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_movie(code: str, title: str, file_id: str, description: str = ""):
    movies = load_movies()
    movies[code.upper()] = {
        "title": title,
        "file_id": file_id,
        "description": description,
        "code": code.upper()
    }
    save_movies(movies)

def get_movie(code: str):
    movies = load_movies()
    return movies.get(code.upper())

def delete_movie(code: str) -> bool:
    movies = load_movies()
    key = code.upper()
    if key in movies:
        del movies[key]
        save_movies(movies)
        return True
    # Agar kod topilmasa, nom bo'yicha qidirish
    for k, v in movies.items():
        if v["title"].lower() == code.lower():
            del movies[k]
            save_movies(movies)
            return True
    return False

def search_movie_by_name(name: str):
    movies = load_movies()
    results = []
    for code, movie in movies.items():
        if name.lower() in movie["title"].lower():
            results.append(movie)
    return results

def get_movies_count() -> int:
    return len(load_movies())

# ───── USERS ─────

def load_users() -> dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"real_users": [], "initial_count": INITIAL_USERS}

def save_users(data: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def register_user(user_id: int, username: str = "", full_name: str = ""):
    data = load_users()
    real_users = data.get("real_users", [])
    ids = [u["id"] for u in real_users]
    if user_id not in ids:
        real_users.append({
            "id": user_id,
            "username": username,
            "full_name": full_name
        })
        data["real_users"] = real_users
        save_users(data)

def get_total_users() -> int:
    data = load_users()
    initial = data.get("initial_count", INITIAL_USERS)
    real = len(data.get("real_users", []))
    return initial + real

def get_all_user_ids() -> list:
    data = load_users()
    return [u["id"] for u in data.get("real_users", [])]

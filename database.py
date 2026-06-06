import json
import os
from config import INITIAL_USERS

MOVIES_FILE = "movies.json"
USERS_FILE = "users.json"

def load_movies():
    if os.path.exists(MOVIES_FILE):
        with open(MOVIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_movies(data):
    with open(MOVIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_movie(code, title, file_id, description=""):
    movies = load_movies()
    movies[code.upper()] = {"title": title, "file_id": file_id, "description": description, "code": code.upper()}
    save_movies(movies)

def get_movie(code):
    return load_movies().get(code.upper())

def delete_movie(query):
    movies = load_movies()
    key = query.upper()
    if key in movies:
        del movies[key]
        save_movies(movies)
        return True
    for k, v in movies.items():
        if v["title"].lower() == query.lower():
            del movies[k]
            save_movies(movies)
            return True
    return False

def search_movie(name):
    return [m for m in load_movies().values() if name.lower() in m["title"].lower()]

def get_movies_count():
    return len(load_movies())

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": [], "initial": INITIAL_USERS}

def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def register_user(user_id, username="", full_name=""):
    data = load_users()
    ids = [u["id"] for u in data["users"]]
    if user_id not in ids:
        data["users"].append({"id": user_id, "username": username, "full_name": full_name})
        save_users(data)

def get_total_users():
    data = load_users()
    return data.get("initial", INITIAL_USERS) + len(data.get("users", []))

def get_all_user_ids():
    return [u["id"] for u in load_users().get("users", [])]

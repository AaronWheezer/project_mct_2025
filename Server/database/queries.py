# Server/database/queries.py

from Server.database.db import get_connection 
from Server.models.user import User

def add_user(name, nickname, email, password):
    user = User.create(name, nickname, email, password)
    return user

def get_all_users():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, nickname, email FROM users")
        users = []
        for row in cursor.fetchall():
            users.append(User(*row))
    return users

def get_user_by_nickname(nickname):
    return User.get_by_nickname(nickname)
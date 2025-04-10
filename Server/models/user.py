# Server/models/user.py
from Server.database.db import get_connection
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class User:
    def __init__(self, id, name, nickname, email, password=None):
        self.id = id
        self.name = name
        self.nickname = nickname
        self.email = email
        self.password = password

    @classmethod
    def create(cls, name, nickname, email, password):
        # Hash the password before saving it
        hashed_password = hash_password(password)
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR IGNORE INTO users (name, nickname, email, password)
            VALUES (?, ?, ?, ?)
            """, (name, nickname, email, hashed_password))
            conn.commit()
        return cls(None, name, nickname, email, password)

    @classmethod
    def get_by_nickname(cls, nickname):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, nickname, email, password FROM users WHERE nickname = ?", (nickname,))
            result = cursor.fetchone()
            if result:
                return cls(*result)
            return None

    def check_password(self, password):
        return self.password == hash_password(password)

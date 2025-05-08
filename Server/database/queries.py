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

def log_search_request(user_id, action):
    """Log een zoekopdracht in de database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO search_requests (user_id, action)
        VALUES (?, ?);
        """, (user_id, action))
        conn.commit()
        
# get list of users and the amount of search requests they made
def get_user_search_requests():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT users.nickname, COUNT(search_requests.id) AS request_count
        FROM users
        LEFT JOIN search_requests ON users.id = search_requests.user_id
        GROUP BY users.id;
        """)
        return cursor.fetchall()
    
#get the most popular search request
def get_all_search_requests_count():
    """Retrieve all search requests grouped by action with their counts."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT action, COUNT(*) AS request_count
        FROM search_requests
        GROUP BY action
        ORDER BY request_count DESC;
        """)
        return cursor.fetchall()
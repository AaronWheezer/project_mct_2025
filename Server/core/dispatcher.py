# Server/core/dispatcher.py
from Server.database.queries import add_user, get_user_by_nickname
from Server.models.user import User

def handle_message(action, data, client_socket):
    if action == "login":
        nickname = data.get("nickname")
        password = data.get("password")

        user = get_user_by_nickname(nickname)
        if user:
            if user.check_password(password):
                client_socket.send("Login successful".encode())
            else:
                client_socket.send("Invalid password.".encode())
        else:
            client_socket.send("User not found.".encode())
    
    elif action == "register":
        name = data.get("name")
        nickname = data.get("nickname")
        email = data.get("email")
        password = data.get("password")

        # Check if the nickname already exists
        if get_user_by_nickname(nickname):
            client_socket.send("Nickname already taken.".encode())
        else:
            add_user(name, nickname, email, password)
            client_socket.send(f"Welcome, {nickname}! You have been registered.".encode())

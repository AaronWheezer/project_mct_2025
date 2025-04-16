# Server/core/dispatcher.py
from Server.database.queries import add_user, get_user_by_nickname
from Server.models.user import User

def handle_message(action, data, client_socket, gui_app):
    if action == "login":
        nickname = data.get("nickname")
        password = data.get("password")

        user = get_user_by_nickname(nickname)
        if user:
            if user.check_password(password):
                client_socket.send("Login successful".encode())
                gui_app.log(f"[LOGIN] {nickname} logged in.")
                return True  # Indicate login was successful
            else:
                client_socket.send("Invalid password.".encode())
                gui_app.log(f"[LOGIN FAILED] Invalid password for {nickname}")
                return False
        else:
            client_socket.send("User not found.".encode())
            gui_app.log(f"[LOGIN FAILED] User not found: {nickname}")
            return False

    elif action == "register":
        name = data.get("name")
        nickname = data.get("nickname")
        email = data.get("email")
        password = data.get("password")

        if get_user_by_nickname(nickname):
            client_socket.send("Nickname already taken.".encode())
            gui_app.log(f"[REGISTER FAILED] Nickname taken: {nickname}")
        else:
            add_user(name, nickname, email, password)
            client_socket.send(f"Welcome, {nickname}! You have been registered.".encode())
            gui_app.log(f"[REGISTER] New user: {nickname} ({email})")

    # Default return for other actions
    return False

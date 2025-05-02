# Server/core/dispatcher.py
from Server.database.queries import add_user, get_user_by_nickname
from Server.models.user import User
from Server.logic.plots import generate_plots
import json
from shared.config import PLOT_DIR
import base64
import struct
def handle_message(action, data, client_socket, gui_app):
    if action == "login":
        nickname = data.get("nickname")
        password = data.get("password")

        user = get_user_by_nickname(nickname)
        if user:
            if user.check_password(password):
                if not isinstance(user, User):
                    user = User(user.id, user.name, user.nickname, user.email)
                    ## reather use a user method for this but no time. // lazzy lol
                response = {
                    "status": "success",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "nickname": user.nickname,
                        "email": user.email
                    }
                }

                client_socket.send(json.dumps(response).encode())
                gui_app.log(f"[LOGIN] {nickname} logged in.")
                return True
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
            return False
                        
    elif action == "get_initial_plots":
        try:
            plots_data = generate_plots()
            plots_json = json.dumps(plots_data)
            encoded = plots_json.encode('utf-8')
            # Send the length of the data first (4 bytes, big-endian)
            client_socket.sendall(struct.pack('>I', len(encoded)))
            # Then send the actual data
            client_socket.sendall(encoded)
            gui_app.log("[INITIAL PLOTS] Plot data sent to the client.")
            return True
        except Exception as e:
            gui_app.log(f"[ERROR] Failed to generate or send plot data: {e}")
            error_json = json.dumps({"error": "Failed to generate plots"}).encode('utf-8')
            client_socket.sendall(struct.pack('>I', len(error_json)))
            client_socket.sendall(error_json)
            return False

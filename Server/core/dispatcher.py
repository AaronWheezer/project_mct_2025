# Server/core/dispatcher.py
from Server.database.queries import add_user, get_user_by_nickname
from Server.models.user import User
from Server.logic.plots import get_plot_images
import json
from shared.config import PLOT_DIR
import base64
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
                
    # Server-side code
    elif action == "get_initial_plots":
        plot_paths = get_plot_images()
        
        # Send the number of plots as 4-byte integer
        client_socket.sendall(len(plot_paths).to_bytes(4, 'big'))  
        
        # Send the paths of the plots one by one
        for path in plot_paths:
            path_bytes = path.encode('utf-8')  # Convert string to bytes
            path_length = len(path_bytes).to_bytes(4, 'big')  # Length of path in bytes
            
            # Send the length and then the actual path
            client_socket.sendall(path_length)  # Send path length
            client_socket.sendall(path_bytes)  # Send path itself as bytes
        
        gui_app.log("[INITIAL PLOTS] User app initialized and plot paths sent.")
        return True

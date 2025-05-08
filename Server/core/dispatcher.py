# Server/core/dispatcher.py
from Server.database.queries import add_user, get_user_by_nickname ,log_search_request
from Server.models.user import User
from Server.logic.plots import generate_plots
from Server.logic.queries import (
    get_arrests_by_descent,
    get_arrests_by_area,
    get_age_distribution,
    get_most_common_crime
)
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
            send_with_length_prefix(client_socket, plots_data)
            gui_app.log("[INITIAL PLOTS] Plot data sent to the client.")
            return True
        except Exception as e:
            gui_app.log(f"[ERROR] Failed to generate or send plot data: {e}")
            send_with_length_prefix(client_socket, {"error": "Failed to generate plots"})
            return False

    elif action == "query_arrests_by_descent":
        try:
            user_id = data.get("user_id")  # Zorg ervoor dat de client het user_id meestuurt
            log_search_request(user_id, action)  # Log de zoekopdracht
            descent_code = data.get("descent_code")
            result = get_arrests_by_descent(descent_code)
            send_with_length_prefix(client_socket, result)
            gui_app.log(f"[QUERY] Arrests by descent code: {descent_code}")
        except Exception as e:
            gui_app.log(f"[ERROR] Failed to process query: {e}")
            send_with_length_prefix(client_socket, {"error": "Failed to process query"})

    elif action == "query_arrests_by_area":
        try:
            user_id = data.get("user_id")  # Zorg ervoor dat de client het user_id meestuurt
            log_search_request(user_id, action)  # Log de zoekopdracht
            area_id = data.get("area_id")
            result = get_arrests_by_area(area_id)
            send_with_length_prefix(client_socket, result)
            gui_app.log(f"[QUERY] Arrests by area: {area_id}")
        except Exception as e:
            gui_app.log(f"[ERROR] Failed to process query: {e}")
            send_with_length_prefix(client_socket, {"error": "Failed to process query"})

    elif action == "query_age_distribution":
        try:
            user_id = data.get("user_id")  # Zorg ervoor dat de client het user_id meestuurt
            log_search_request(user_id, action)  # Log de zoekopdracht
            result = get_age_distribution()
            send_with_length_prefix(client_socket, result)
            gui_app.log("[QUERY] Age distribution")
        except Exception as e:
            gui_app.log(f"[ERROR] Failed to process query: {e}")
            send_with_length_prefix(client_socket, {"error": "Failed to process query"})

    elif action == "query_most_common_crime":
        try:
            user_id = data.get("user_id")  # Zorg ervoor dat de client het user_id meestuurt
            log_search_request(user_id, action)  # Log de zoekopdracht
            filter_value = data.get("filter")
            result = get_most_common_crime(filter_value)
            send_with_length_prefix(client_socket, result)
            gui_app.log(f"[QUERY] Most common crime with filter: {filter_value}")
        except Exception as e:
            gui_app.log(f"[ERROR] Failed to process query: {e}")
            send_with_length_prefix(client_socket, {"error": "Failed to process query"})

def send_with_length_prefix(client_socket, data):
    """Send data with a length prefix."""
    try:
        json_data = json.dumps(data).encode('utf-8')
        print(f"[DEBUG] Sending data: {json_data.decode('utf-8')}")
        print(f"[DEBUG] Length of JSON data: {len(json_data)}")
        # Send the length of the data first (4 bytes, big-endian)
        client_socket.sendall(struct.pack('>I', len(json_data)))
        # Then send the actual data
        client_socket.sendall(json_data)
    except Exception as e:
        print(f"[ERROR] Failed to send data with length prefix: {e}")
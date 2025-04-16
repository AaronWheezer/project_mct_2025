# Server/core/handler.py
from shared.protocol import parse_message
from Server.core.dispatcher import handle_message

def handle_client(client_socket, client_address, gui_app):
    nickname = None  # Track the nickname of the client once they login

    try:
        while True:
            raw = client_socket.recv(1024).decode()
            if not raw:
                break  # Client disconnected
            
            msg = parse_message(raw)
            action = msg.get("action")
            data = msg.get("data")
            
            gui_app.log(f"[REQUEST] From {client_address}: {action}")

            # Login special handling
            if action == "login":
                nickname = data.get("nickname")
                success = handle_message(action, data, client_socket, gui_app)

                if success:
                    # Avoid duplicates
                    if not any(client['socket'] == client_socket for client in gui_app.clients):
                        gui_app.clients.append({"username": nickname, "socket": client_socket})
                        gui_app.log(f"[CONNECTED] {client_address} as {nickname}")
                        gui_app.refresh_users_tabs()
                continue  # Skip re-calling the dispatcher

            # Handle all other actions
            handle_message(action, data, client_socket, gui_app)

    except Exception as e:
        gui_app.log(f"[ERROR] {client_address}: {e}")

    finally:
        client_socket.close()

        # Remove disconnected client from active list
        gui_app.clients[:] = [client for client in gui_app.clients if client['socket'] != client_socket]
        gui_app.log(f"[DISCONNECTED] {client_address}")

        gui_app.refresh_users_tabs()

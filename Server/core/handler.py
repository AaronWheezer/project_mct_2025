# Server/core/handler.py
from shared.protocol import parse_message
from Server.core.dispatcher import handle_message

# Server/core/handler.py
from shared.protocol import parse_message
from Server.core.dispatcher import handle_message

def handle_client(client_socket, client_address, gui_app):
    while True:
        try:
            raw = client_socket.recv(1024).decode()
            if not raw:
                break
            msg = parse_message(raw)
            gui_app.log(f"[REQUEST] From {client_address}: {msg['action']}")  # Log action
            handle_message(msg['action'], msg['data'], client_socket, gui_app)
        except Exception as e:
            gui_app.log(f"[ERROR] {client_address}: {e}")
            break
    client_socket.close()
    gui_app.log(f"[DISCONNECTED] {client_address}")

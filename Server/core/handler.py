# Server/core/handler.py
from shared.protocol import parse_message
from Server.core.dispatcher import handle_message

def handle_client(client_socket, client_address):
    while True:
        try:
            raw = client_socket.recv(1024).decode()
            if not raw:
                break
            msg = parse_message(raw)
            handle_message(msg['action'], msg['data'], client_socket)
        except Exception as e:
            print(f"[ERROR] {client_address}: {e}")
            break
    client_socket.close()

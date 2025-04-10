import socket
import threading
from shared.config import HOST, PORT
from Server.core.handler import handle_client
from Server.database.db import init_db  
def start_server():
    init_db() 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[SERVER] Listening on {HOST}:{PORT}...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"[CONNECTED] {client_address}")
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()

if __name__ == "__main__":
    start_server()

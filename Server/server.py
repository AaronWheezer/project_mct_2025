import socket
import threading
from Server.database.db import init_db  
from shared.config import HOST, PORT
from Server.core.handler import handle_client
from Server.gui.server_gui import start_gui

gui_app = None

def start_server():
    init_db() 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    gui_app.log(f"[SERVER] Listening on {HOST}:{PORT}...")

    while True:
        client_socket, client_address = server_socket.accept()
        gui_app.log(f"[CONNECTED] {client_address}")
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address, gui_app))
        thread.start()

if __name__ == "__main__":
    gui_app, root = start_gui()
    threading.Thread(target=start_server, daemon=True).start()
    root.mainloop()

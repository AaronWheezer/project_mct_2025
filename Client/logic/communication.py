# Client/logic/connection.py

import socket
import json
from shared.config import HOST, PORT, BUFFER_SIZE
# Client/logic/communication.py# Client/logic/communication.py
class ClientConnection:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.username = None  # Initially, no username

    def send(self, action, data):
        try:
            message = json.dumps({"action": action, "data": data})
            self.sock.sendall(message.encode())
            response = self.sock.recv(BUFFER_SIZE).decode()
            return response
        except Exception as e:
            return f"Error: {e}"

    def close(self):
        self.sock.close()


    def listen_to_server(self, callback_on_disconnect):
        try:
            while True:
                data = self.sock.recv(BUFFER_SIZE)
                if not data:
                    break  # Disconnected
        except (ConnectionResetError, OSError):
            pass
        callback_on_disconnect()
        
    def receive(self, size=1024):
        """Receive a specific number of bytes from the socket."""
        try:
            data = self.sock.recv(size)
            return data.decode()  # Decode to string
        except Exception as e:
            print(f"[ERROR] Receiving data failed: {e}")
            return ""

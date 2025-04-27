import socket
import json
from tkinter import messagebox
import threading
from shared.config import HOST, PORT, BUFFER_SIZE

class ClientConnection:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.username = None  # Initially, no username
        self.listener_thread = None  # Add this line to track the thread

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
        """Listen to the server in a separate thread."""
        if self.listener_thread is None or not self.listener_thread.is_alive():  # Check if the listener is already running
            def listen():
                try:
                    while True:
                        print("Waiting for data...")
                        data = self.sock.recv(BUFFER_SIZE).decode()
                        if not data:
                            break  # Disconnected
                        # Handle broadcast messages
                        if data.startswith("[BROADCAST]"):
                            print(f"[BROADCAST] {data[len('[BROADCAST]'):]}")  # Ensure message is being handled
                            messagebox.showinfo("Broadcast Message", data[len("[BROADCAST]"):])
                except (ConnectionResetError, OSError) as e:
                    print(f"Connection error: {e}")
                callback_on_disconnect()

            self.listener_thread = threading.Thread(target=listen, daemon=True)  # Ensure the thread is marked as a daemon thread
            self.listener_thread.start()
            
    def receive(self, size=1024):
        """Receive a specific number of bytes from the socket."""
        try:
            data = self.sock.recv(size)
            return data.decode()  # Decode to string
        except Exception as e:
            print(f"[ERROR] Receiving data failed: {e}")
            return ""

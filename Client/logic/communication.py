import socket
import json
from tkinter import messagebox
import threading
from shared.config import HOST, PORT, BUFFER_SIZE
import struct

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
            # Only receive a response for actions that expect a simple reply
            if action not in ["get_initial_plots"]:
                response = self.sock.recv(BUFFER_SIZE).decode()
                return response
            # For get_initial_plots, the caller should use receive_json()
            return None
        except Exception as e:
            return f"Error: {e}"

    def close(self):
        self.sock.close()

    def listen_to_server(self, callback_on_disconnect):
        """Listen to the server in a separate thread for general messages."""
        if self.listener_thread is None or not self.listener_thread.is_alive():
            def listen():
                try:
                    while True:
                        print("Waiting for data...")
                        data = self.sock.recv(BUFFER_SIZE).decode()  # Decode as text
                        if not data:
                            break  # Disconnected
                        # Handle broadcast messages
                        if data.startswith("[BROADCAST]"):
                            print(f"[BROADCAST] {data[len('[BROADCAST]'):]}")  # Ensure message is being handled
                            messagebox.showinfo("Broadcast Message", data[len("[BROADCAST]"):])
                except (ConnectionResetError, OSError) as e:
                    print(f"Connection error: {e}")
                callback_on_disconnect()

            self.listener_thread = threading.Thread(target=listen, daemon=True)
            self.listener_thread.start()
            
    def receive_json(self):
        try:
            # Receive the length prefix (4 bytes)
            raw_len = self.sock.recv(4)
            print(f"[DEBUG] Raw length received: {raw_len}")
            if not raw_len or len(raw_len) < 4:
                print("[ERROR] Failed to receive length prefix.")
                return None
            msg_len = struct.unpack('>I', raw_len)[0]
            print(f"[DEBUG] Expected message length: {msg_len}")
            # Receive the actual JSON data
            buffer = b""
            while len(buffer) < msg_len:
                chunk = self.sock.recv(msg_len - len(buffer))
                if not chunk:
                    print("[ERROR] Connection closed before all data received.")
                    return None
                buffer += chunk
            return buffer.decode('utf-8')
        except Exception as e:
            print(f"[ERROR] Receiving JSON data failed: {e}")
            return None
        
    def receiveJSONSimple(self):
        """Receive JSON data without length prefix."""
        try:
            data = self.sock.recv(BUFFER_SIZE).decode()
            if not data:
                print("[ERROR] No data received.")
                return None
            return json.loads(data)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON decoding failed: {e}")
            return None
        except Exception as e:
            print(f"[ERROR] Receiving data failed: {e}")
            return None
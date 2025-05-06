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
            if action not in ["get_initial_plots"] and not action.startswith("query"):
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
        """Receive JSON data with a length prefix."""
        try:
            # Receive the length prefix (4 bytes)
            raw_len = self.sock.recv(4)
            if not raw_len or len(raw_len) < 4:
                print("[ERROR] Failed to receive length prefix.")
                return None
            print(f"[DEBUG] Raw length prefix: {raw_len}")
            msg_len = struct.unpack('>I', raw_len)[0]
            print(f"[DEBUG] Expected message length: {msg_len}")

            # Sanity check for message length
            if msg_len <= 0 or msg_len > 10**6:  # Limit to 1 MB
                print("[ERROR] Invalid message length received.")
                return None

            # Receive the actual JSON data
            buffer = b""
            while len(buffer) < msg_len:
                chunk = self.sock.recv(msg_len - len(buffer))
                if not chunk:
                    print("[ERROR] Connection closed before all data received.")
                    return None
                buffer += chunk

            # Decode and return the JSON data
            json_data = buffer.decode('utf-8')
            print(f"[DEBUG] Received raw data: {json_data}")
            return json_data
        except Exception as e:
            print(f"[ERROR] Receiving JSON data failed: {e}")
            return None
    def query_json_receive(self):
        """Receive JSON data without relying on a length prefix and handle errors gracefully."""
        try:
            # Read data from the socket until the end of the message
            buffer = b""
            while True:
                chunk = self.sock.recv(BUFFER_SIZE)
                if not chunk:
                    print("[ERROR] Connection closed before all data received.")
                    return None
                buffer += chunk

                # Try to decode the buffer as JSON
                try:
                    json_data = buffer.decode('utf-8')
                    parsed_data = json.loads(json_data)  # Parse JSON into a Python dictionary
                    print(f"[DEBUG] Received JSON data: {parsed_data}")

                    # Check if the response contains an error
                    if "error" in parsed_data:
                        print(f"[ERROR] Server returned an error: {parsed_data['error']}")
                        return {"error": parsed_data["error"]}

                    # Return the parsed data if no error is present
                    return parsed_data
                except json.JSONDecodeError:
                    # If decoding fails, continue reading more data
                    continue
        except Exception as e:
            print(f"[ERROR] Receiving JSON data failed: {e}")
            return {"error": str(e)}
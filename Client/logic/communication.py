# Client/logic/communication.py

import socket
import json
# get host and port from Shared/config.py
from shared.config import HOST, PORT, BUFFER_SIZE

def send_message(action, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        message = json.dumps({"action": action, "data": data})
        client_socket.send(message.encode())
        response = client_socket.recv(BUFFER_SIZE).decode()
    return response

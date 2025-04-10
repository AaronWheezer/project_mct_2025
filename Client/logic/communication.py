# Client/logic/communication.py

import socket
import json

HOST = 'localhost'
PORT = 12345

def send_message(action, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        message = json.dumps({"action": action, "data": data})
        client_socket.send(message.encode())
        response = client_socket.recv(1024).decode()
    return response

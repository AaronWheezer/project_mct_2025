# Client/gui/register.py

import tkinter as tk
from tkinter import messagebox
from Client.logic.communication import send_message

class RegisterWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Register")

        self.name_label = tk.Label(self.root, text="Name")
        self.name_label.pack()
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack()

        self.nickname_label = tk.Label(self.root, text="Nickname")
        self.nickname_label.pack()
        self.nickname_entry = tk.Entry(self.root)
        self.nickname_entry.pack()

        self.email_label = tk.Label(self.root, text="Email")
        self.email_label.pack()
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack()

        self.password_label = tk.Label(self.root, text="Password")
        self.password_label.pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        self.register_button = tk.Button(self.root, text="Register", command=self.register)
        self.register_button.pack()

    def register(self):
        name = self.name_entry.get()
        nickname = self.nickname_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not name or not nickname or not email or not password:
            messagebox.showwarning("Input Error", "All fields are required!")
            return

        response = send_message("register", {"name": name, "nickname": nickname, "email": email, "password": password})
        messagebox.showinfo("Registration", response)
        self.root.destroy()

def open_register_window(root):
    register_window = tk.Toplevel(root)
    register_window_obj = RegisterWindow(register_window)
    register_window.mainloop()

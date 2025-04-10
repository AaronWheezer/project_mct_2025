# Client/gui/main_window.py

import tkinter as tk
from tkinter import messagebox
from Client.logic.communication import send_message
from Client.gui.register import open_register_window

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")

        self.nickname_label = tk.Label(self.root, text="Nickname")
        self.nickname_label.pack()
        self.nickname_entry = tk.Entry(self.root)
        self.nickname_entry.pack()

        self.password_label = tk.Label(self.root, text="Password")
        self.password_label.pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(self.root, text="Login", command=self.login)
        self.login_button.pack()

        self.register_button = tk.Button(self.root, text="Register", command=self.open_register_window)
        self.register_button.pack()

    def login(self):
        nickname = self.nickname_entry.get()
        password = self.password_entry.get()

        if not nickname or not password:
            messagebox.showwarning("Input Error", "Both fields are required!")
            return

        response = send_message("login", {"nickname": nickname, "password": password})
        if response == "Login successful":
            messagebox.showinfo("Login", response)
        else:
            messagebox.showerror("Login Failed", response)

    def open_register_window(self):
        open_register_window(self.root)

def start_gui():
    root = tk.Tk()
    main_window = MainWindow(root)
    root.mainloop()

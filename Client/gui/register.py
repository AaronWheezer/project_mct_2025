import tkinter as tk
from tkinter import messagebox
from Client.logic.communication import ClientConnection
from shared.theme import THEME

class RegisterFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME["bg"])
        self.controller = controller
        self.connection = ClientConnection()
        self.pack_widgets()

    def pack_widgets(self):
        tk.Label(self, text="Register", font=("Segoe UI", 16, "bold"),
                 bg=THEME["bg"], fg=THEME["fg"]).pack(pady=20)

        self.name_entry = self.create_entry("Name")
        self.nickname_entry = self.create_entry("Nickname")
        self.email_entry = self.create_entry("Email")
        self.password_entry = self.create_entry("Password", show="*")

        tk.Button(self, text="Register", bg=THEME["accent"], fg="white", font=THEME["font"],
                  activebackground=THEME["accent_hover"], command=self.register).pack(pady=10, ipadx=40)

        tk.Button(self, text="Login instead?", bg=THEME["bg"], fg=THEME["accent"], borderwidth=0,
                  font=("Segoe UI", 10, "underline"), activeforeground=THEME["accent_hover"],
                  command=self.show_login).pack(pady=10)

    def create_entry(self, label_text, show=None):
        tk.Label(self, text=label_text, bg=THEME["bg"], fg=THEME["fg"], font=THEME["font"]).pack(pady=(10, 2))
        entry = tk.Entry(self, bg=THEME["entry_bg"], fg=THEME["fg"], insertbackground="white",
                         font=THEME["font"], relief=tk.FLAT, width=THEME["entry_width"], show=show)
        entry.pack(ipady=5)
        return entry

    def register(self):
        name = self.name_entry.get()
        nickname = self.nickname_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not name or not nickname or not email or not password:
            messagebox.showwarning("Input Error", "All fields are required!")
            return

        response =  self.connection.send("register", {
            "name": name,
            "nickname": nickname,
            "email": email,
            "password": password
        })

        messagebox.showinfo("Registration", response)
        if "Welcome" in response:
            from Client.gui.login import LoginFrame  # Lazy import to avoid circular import
            self.controller.show_frame(LoginFrame)

    def show_login(self):
        from Client.gui.login import LoginFrame  # Lazy import to avoid circular import
        self.controller.show_frame(LoginFrame)

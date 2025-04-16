import tkinter as tk
from tkinter import messagebox
from Client.logic.communication import ClientConnection
from Client.gui.theme import THEME
from Client.gui.app_gui import start_app_gui  # Import the AppGUI class

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME["bg"])
        self.controller = controller
        self.pack_widgets()
        self.connection = ClientConnection()

    def pack_widgets(self):
        tk.Label(self, text="Login", font=("Segoe UI", 16, "bold"),
                 bg=THEME["bg"], fg=THEME["fg"]).pack(pady=20)

        self.nickname_entry = self.create_entry("Nickname")
        self.password_entry = self.create_entry("Password", show="*")

        tk.Button(self, text="Login", bg=THEME["accent"], fg="white", font=THEME["font"],
                  activebackground=THEME["accent_hover"], command=self.login).pack(pady=10, ipadx=40)

        tk.Button(self, text="Register instead?", bg=THEME["bg"], fg=THEME["accent"], borderwidth=0,
                  font=("Segoe UI", 10, "underline"), activeforeground=THEME["accent_hover"],
                  command=self.show_register).pack(pady=10)

    def create_entry(self, label_text, show=None):
        tk.Label(self, text=label_text, bg=THEME["bg"], fg=THEME["fg"], font=THEME["font"]).pack(pady=(10, 2))
        entry = tk.Entry(self, bg=THEME["entry_bg"], fg=THEME["fg"], insertbackground="white",
                         font=THEME["font"], relief=tk.FLAT, width=THEME["entry_width"], show=show)
        entry.pack(ipady=5)
        return entry

    def login(self):
        nickname = self.nickname_entry.get()
        password = self.password_entry.get()

        if not nickname or not password:
            messagebox.showwarning("Input Error", "Both fields are required!")
            return

        response = self.connection.send("login", {"nickname": nickname, "password": password})
        if response == "Login successful":
            # Clear the current window and start the main application GUI
            for widget in self.controller.winfo_children():
                widget.destroy()  # Destroy all widgets in the current window

            start_app_gui(self.controller, self.connection)  # Start the app GUI in the same window
        else:
            messagebox.showerror("Login Failed", response)

    def show_register(self):
        from Client.gui.register import RegisterFrame  # Lazy import to avoid circular import
        self.controller.show_frame(RegisterFrame)

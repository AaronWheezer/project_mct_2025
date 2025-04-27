import tkinter as tk
from tkinter import messagebox
from Client.logic.communication import ClientConnection
from shared.theme import THEME
from Client.gui.app_gui import start_app_gui  # Import the AppGUI class
from Client.models.user import User
import json
import threading

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME["bg"])
        self.controller = controller
        self.pack_widgets()
        self.connection = ClientConnection()
        
        # Start the connection listener in a background thread
        # if not self.connection.listener_thread or not self.connection.listener_thread.is_alive():
        #     threading.Thread(target=self.connection.listen_to_server, args=(self.handle_disconnect,), daemon=True).start()

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

        # Parse the response to a dictionary if it's a JSON string
        try:
            if isinstance(response, str):
                response = json.loads(response)  # Convert JSON string to dictionary
        except json.JSONDecodeError as e:
            print("Error parsing JSON response:", e)
            response = {}

        # Now check the response
        if isinstance(response, dict) and response.get("status") == "success" and "user" in response:
            user_data = response["user"]
            self.logged_in_user = User(
                id=user_data["id"],
                name=user_data["name"],
                nickname=user_data["nickname"],
                email=user_data["email"]
            )
            for widget in self.controller.winfo_children():
                widget.destroy()  # Destroy all widgets in the current window

            start_app_gui(self.controller, self.connection ,self.logged_in_user)  # Start the app GUI in the same window
        else:
            messagebox.showerror("Login Failed", "Invalid login credentials. Please try again.")

    def show_register(self):
        from Client.gui.register import RegisterFrame  # Lazy import to avoid circular import
        self.controller.show_frame(RegisterFrame)
        
    def handle_disconnect(self):
        # Handle what happens when the client gets disconnected
        print("Disconnected from server.")
        messagebox.showwarning("Disconnected", "You have been disconnected from the server.")
        self.controller.after(0, self.show_login_frame)  # Safely update the UI on the main thread
        
    def show_login_frame(self):
        from Client.gui.login import LoginFrame  # Re-import to avoid circular import
        self.controller.show_frame(LoginFrame)  # Show login frame again

# Server/gui/main_gui.py
import tkinter as tk
from tkinter import ttk
from Server.database.queries import get_all_users
from Server.models.user import User

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Server Control Panel")
        self.root.geometry("700x500")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.log_frame = ttk.Frame(self.notebook)
        self.users_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.log_frame, text="Logs")
        self.notebook.add(self.users_frame, text="Users")

        self.setup_log_tab()
        self.setup_users_tab()

        self.shutdown_button = tk.Button(root, text="Shutdown Server", command=self.shutdown_server, bg="red", fg="white")
        self.shutdown_button.pack(pady=10)

    def setup_log_tab(self):
        self.log_text = tk.Text(self.log_frame, state="disabled", wrap="word")
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def setup_users_tab(self):
        self.users_tree = ttk.Treeview(self.users_frame, columns=("ID", "Name", "Nickname", "Email"), show="headings")
        for col in ("ID", "Name", "Nickname", "Email"):
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, stretch=True)
        self.users_tree.pack(fill=tk.BOTH, expand=True)
        self.refresh_users()

    def refresh_users(self):
        for row in self.users_tree.get_children():
            self.users_tree.delete(row)
        users = get_all_users()
        for user in users:
            self.users_tree.insert("", "end", values=(user.id, user.name, user.nickname, user.email))

    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)

    def shutdown_server(self):
        self.log("[SERVER] Shutting down...")
        self.root.after(1000, self.root.quit)

def start_gui():
    root = tk.Tk()
    app = ServerGUI(root)
    return app, root

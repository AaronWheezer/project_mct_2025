import tkinter as tk
from tkinter import ttk
from Server.database.queries import get_all_users
from Server.models.user import User
import socket

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Server Control Panel")
        self.root.geometry("800x600")
        self.clients = [] # List to keep track of connected clients
        
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
        # Refresh button
        refresh_btn = tk.Button(self.users_frame, text="Refresh", command=self.refresh_users_tabs, bg="#4CAF50", fg="white")
        refresh_btn.pack(pady=5)

        # Online Users Label
        online_label = tk.Label(self.users_frame, text="Online Users", font=("Segoe UI", 12, "bold"))
        online_label.pack()

        # Tree for online users
        self.online_users_tree = ttk.Treeview(self.users_frame, columns=("Username",), show="headings", height=5)
        self.online_users_tree.heading("Username", text="Username")
        self.online_users_tree.column("Username", width=200)
        self.online_users_tree.pack(pady=5, fill=tk.X, padx=10)

        # Separator
        ttk.Separator(self.users_frame, orient='horizontal').pack(fill='x', pady=10)

        # All Users Label
        all_label = tk.Label(self.users_frame, text="All Registered Users", font=("Segoe UI", 12, "bold"))
        all_label.pack()

        # Tree for all users
        self.all_users_tree = ttk.Treeview(self.users_frame, columns=("ID", "Name", "Nickname", "Email"), show="headings", height=10)
        for col in ("ID", "Name", "Nickname", "Email"):
            self.all_users_tree.heading(col, text=col)
            self.all_users_tree.column(col, stretch=True)
        self.all_users_tree.pack(fill=tk.BOTH, expand=True, padx=10)

        # Load initial data
        self.refresh_users_tabs()

    def refresh_users_tabs(self):
        self.refresh_online_users()
        self.refresh_all_users()

    def refresh_online_users(self):
        self.online_users_tree.delete(*self.online_users_tree.get_children())
        for client in self.clients:
            if client.get("username") and client.get("socket"):
                sock = client['socket']
                if sock.fileno() != -1:  # Check if socket is open
                    self.online_users_tree.insert("", "end", values=(client['username'],))

    def refresh_all_users(self):
        self.all_users_tree.delete(*self.all_users_tree.get_children())
        users = get_all_users()
        for user in users:
            self.all_users_tree.insert("", "end", values=(user.id, user.name, user.nickname, user.email))

    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)

    def shutdown_server(self):
        self.log("[SERVER] Shutting down...")

        for client in self.clients:
            try:
                if client['socket'].fileno() != -1:
                    print(f"Shutting down connection for {client['username']}")
                    client['socket'].shutdown(socket.SHUT_RDWR)
                    client['socket'].close()
                else:
                    print(f"Socket for {client['username']} already closed.")
            except Exception as e:
                self.log(f"[ERROR] Could not close client socket for {client['username']}: {e}")
        
        self.root.after(1000, self.root.quit)

def start_gui():
    root = tk.Tk()
    app = ServerGUI(root)
    return app, root

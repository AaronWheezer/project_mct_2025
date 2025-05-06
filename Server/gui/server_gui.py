import tkinter as tk
from tkinter import ttk
from Server.database.queries import get_all_users
from Server.models.user import User
from shared.theme import THEME
import socket

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Server Control Panel")
        self.root.geometry("800x600")
        self.root.configure(bg=THEME["bg"])
        self.clients = []  # List to keep track of connected clients

        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=THEME["bg"])
        style.configure("TFrame", background=THEME["bg"])
        style.configure("Treeview", background=THEME["entry_bg"], foreground=THEME["fg"], fieldbackground=THEME["entry_bg"], font=THEME["font"])
        style.configure("Treeview.Heading", background=THEME["accent"], foreground="white", font=(THEME["font"][0], 11, "bold"))
        style.map("Treeview", background=[("selected", THEME["accent_hover"])])

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.log_frame = ttk.Frame(self.notebook)
        self.users_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.log_frame, text="Logs")
        self.notebook.add(self.users_frame, text="Users")

        self.setup_log_tab()
        self.setup_users_tab()
        self.setup_message_tab()

        self.shutdown_button = tk.Button(
            root,
            text="Shutdown Server",
            command=self.shutdown_server,
            bg="red",
            fg="white",
            font=THEME["font"]
        )
        self.shutdown_button.pack(pady=10)

    def setup_log_tab(self):
        self.log_text = tk.Text(
            self.log_frame,
            state="disabled",
            wrap="word",
            bg=THEME["entry_bg"],
            fg=THEME["fg"],
            font=THEME["font"]
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def setup_message_tab(self):
        """Set up the 'Message' tab in the GUI."""
        self.message_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.message_frame, text="Message")

        # Message input field
        self.message_entry = tk.Entry(self.message_frame, font=("Segoe UI", 12), bg="lightgray", fg="black")
        self.message_entry.pack(pady=10, padx=10, fill=tk.X)

        # Send message button
        self.send_button = tk.Button(
            self.message_frame,
            text="Send Message",
            font=("Segoe UI", 12, "bold"),
            bg="blue",
            fg="white",
            command=self.send_broadcast_message
        )
        self.send_button.pack(pady=10)

        # Online users label
        self.online_users_label = tk.Label(
            self.message_frame,
            text="Online Users:",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="black"
        )
        self.online_users_label.pack(pady=10)

        # Online users Treeview for Message tab
        self.online_users_tree_message = ttk.Treeview(
            self.message_frame,
            columns=("Username",),
            show="headings",
            height=5
        )
        self.online_users_tree_message.heading("Username", text="Username")
        self.online_users_tree_message.column("Username", width=200)
        self.online_users_tree_message.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def setup_users_tab(self):
        # Header row with label and refresh button
        header_frame = tk.Frame(self.users_frame, bg=THEME["bg"])
        header_frame.pack(fill="x", pady=(20, 10), padx=30)

        online_label = tk.Label(
            header_frame,
            text="Online users",
            font=(THEME["font"][0], 16, "bold"),
            bg=THEME["bg"],
            fg="white"
        )
        online_label.pack(side="left")

        refresh_btn = tk.Button(
            header_frame,
            text="Refresh  ⟳",
            command=self.refresh_users_tabs,
            bg=THEME["accent"],
            fg="white",
            activebackground=THEME["accent_hover"],
            font=(THEME["font"][0], 12, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=4,
            highlightthickness=0,
            cursor="hand2"
        )
        refresh_btn.pack(side="right", padx=(0, 10))

        # Online users pill/card list
        self.online_users_card_frame = tk.Frame(self.users_frame, bg=THEME["bg"])
        self.online_users_card_frame.pack(fill="x", padx=30, pady=(0, 20))

        # Separator
        ttk.Separator(self.users_frame, orient='horizontal').pack(fill='x', pady=10, padx=30)

        # All users section (keep your existing Treeview for all users)
        all_label = tk.Label(
            self.users_frame,
            text="All Registered Users",
            font=(THEME["font"][0], 12, "bold"),
            bg=THEME["bg"],
            fg="white"
        )
        all_label.pack(padx=30, anchor="w")

        self.all_users_tree = ttk.Treeview(
            self.users_frame,
            columns=("ID", "Name", "Nickname", "Email"),
            show="headings",
            height=10
        )
        for col in ("ID", "Name", "Nickname", "Email"):
            self.all_users_tree.heading(col, text=col)
            self.all_users_tree.column(col, stretch=True)
        self.all_users_tree.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))

        self.refresh_users_tabs()

    def refresh_users_tabs(self):
        self.refresh_online_users()
        self.refresh_all_users()

    def send_broadcast_message(self):
        """Send the message entered in the input field to all connected clients."""
        message = self.message_entry.get()
        if message:
            self.broadcast_message(message)
            self.message_entry.delete(0, tk.END)  # Clear the input field

    def broadcast_message(self, message):
        """Send a message to all connected clients."""
        for client in self.clients:
            print(f"[BROADCAST] Sending message to {client['username']}")
            try:
                if client['socket'].fileno() != -1:  # Check if the socket is still open
                    print(f"[BROADCAST] open socket {client['username']}")
                    client['socket'].sendall(f"[BROADCAST] {message}".encode())
            except Exception as e:
                print(f"[ERROR] Could not send message to {client['username']}: {e}")

    def refresh_online_users(self):
        # Clear previous cards
        for widget in self.online_users_card_frame.winfo_children():
            widget.destroy()
        # Add a pill/card for each online user
        for client in self.clients:
            if client.get("username") and client.get("socket"):
                sock = client['socket']
                if sock.fileno() != -1:
                    self._add_online_user_card(client['username'])

    def _add_online_user_card(self, username):
        card = tk.Frame(
            self.online_users_card_frame,
            bg=THEME["card_bg"],
            bd=0,
            relief="flat",
            highlightbackground=THEME["bg"],
            highlightthickness=0
        )
        card.pack(fill="x", pady=6, padx=0)

        name_label = tk.Label(
            card,
            text=username,
            font=(THEME["font"][0], 13, "bold"),
            bg=THEME["accent"],
            fg="white",
            padx=18,
            pady=6,
            bd=0,
            relief="flat"
        )
        name_label.pack(side="left", padx=(10, 0), pady=4)

        close_btn = tk.Button(
            card,
            text="✕",
            font=(THEME["font"][0], 13, "bold"),
            bg=THEME["card_bg"],
            fg="white",
            activebackground=THEME["accent_hover"],
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=10,
            pady=2,
            cursor="hand2",
            command=lambda: self.kick_user(username)
        )
        close_btn.pack(side="left", padx=(10, 10), pady=4)

    def kick_user(self, username):
        # Optional: implement kicking logic
        print(f"[KICK] User {username} would be kicked here.")
        #disconnect the user from the server
        for client in self.clients:
            if client.get("username") == username:
                try:
                    if client['socket'].fileno() != -1:
                        client['socket'].shutdown(socket.SHUT_RDWR)
                        client['socket'].close()
                        self.log(f"[KICK] User {username} has been kicked.")
                except Exception as e:
                    self.log(f"[ERROR] Could not kick user {username}: {e}")
                break
        # Optionally, remove the user from the clients list
        # You can close the socket or remove from self.clients as needed

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
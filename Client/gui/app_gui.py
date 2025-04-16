import tkinter as tk
from tkinter import ttk
from Client.logic.communication import send_message
from Client.gui.theme import THEME

class AppGUI(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME["bg"])
        self.controller = controller
        self.pack(fill="both", expand=True)
        
        # Keep connection with the server (signifying user is online)
        #self.keep_online()
        toplevel = self.winfo_toplevel()
        toplevel.geometry("1000x700")  # Resize here
        # Set up the tabs
        self.tab_control = ttk.Notebook(self)

        self.home_tab = tk.Frame(self.tab_control, bg=THEME["bg"])
        self.query_tab = tk.Frame(self.tab_control, bg=THEME["bg"])
        self.profile_tab = tk.Frame(self.tab_control, bg=THEME["bg"])

        self.tab_control.add(self.home_tab, text="Home")
        self.tab_control.add(self.query_tab, text="Search Queries")
        self.tab_control.add(self.profile_tab, text="Profile")
        
        self.tab_control.pack(expand=1, fill="both")

        # Home Tab Content
        self.home_label = tk.Label(self.home_tab, text="Welcome to the Client App", font=("Segoe UI", 18, "bold"), bg=THEME["bg"], fg=THEME["fg"])
        self.home_label.pack(pady=20)

        # Query Tab Content
        self.query_label = tk.Label(self.query_tab, text="Search Queries", font=("Segoe UI", 16, "bold"), bg=THEME["bg"], fg=THEME["fg"])
        self.query_label.pack(pady=20)

        # Profile Tab Content
        self.profile_label = tk.Label(self.profile_tab, text="Profile Information", font=("Segoe UI", 16, "bold"), bg=THEME["bg"], fg=THEME["fg"])
        self.profile_label.pack(pady=20)

    def keep_online(self):
        # Send a message to the server to indicate user is online
        send_message("update_status", {"status": "online"})
        
def start_app_gui(root):
    app = AppGUI(root, None)
    root.mainloop()

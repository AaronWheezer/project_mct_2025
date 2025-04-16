import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from Client.logic.communication import ClientConnection
from shared.theme import THEME

class AppGUI(tk.Frame):
    def __init__(self, parent, controller, connection):
        super().__init__(parent, bg=THEME["bg"])
        self.controller = controller
        self.pack(fill="both", expand=True)
        self.connection = connection
        
        # Keep connection with the server (signifying user is online)
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

        # Query 1: Number of arrests per time period
        self.time_period_label = tk.Label(self.query_tab, text="Time Period (e.g., 'month' or 'week')", bg=THEME["bg"], fg=THEME["fg"])
        self.time_period_label.pack(pady=5)
        self.time_period_entry = tk.Entry(self.query_tab, bg=THEME["bg"], fg=THEME["fg"])
        self.time_period_entry.pack(pady=5)

        # Query 2: Arrests per area
        self.area_label = tk.Label(self.query_tab, text="Area ID", bg=THEME["bg"], fg=THEME["fg"])
        self.area_label.pack(pady=5)
        self.area_entry = tk.Entry(self.query_tab, bg=THEME["bg"], fg=THEME["fg"])
        self.area_entry.pack(pady=5)

        # Query 3: Age distribution of arrests
        self.age_distribution_label = tk.Label(self.query_tab, text="Age Distribution", bg=THEME["bg"], fg=THEME["fg"])
        self.age_distribution_label.pack(pady=5)
        self.age_distribution_button = tk.Button(self.query_tab, text="Show Age Distribution", bg=THEME["bg"], fg=THEME["fg"], command=self.show_age_distribution)  # TODO: implement function
        self.age_distribution_button.pack(pady=5)

        # Query 4: Most common crime description
        self.crime_label = tk.Label(self.query_tab, text="Most Common Crime Description", bg=THEME["bg"], fg=THEME["fg"])
        self.crime_label.pack(pady=5)
        self.crime_button = tk.Button(self.query_tab, text="Show Most Common Crime", bg=THEME["bg"], fg=THEME["fg"], command=self.show_common_crime)  # TODO: implement function
        self.crime_button.pack(pady=5)

        # Results Frame
        self.results_frame = tk.Frame(self.query_tab, bg=THEME["bg"])
        self.results_frame.pack(pady=20, fill="both", expand=True)

        self.results_label = tk.Label(self.results_frame, text="Results will appear here", font=("Segoe UI", 14), bg=THEME["bg"], fg=THEME["fg"])
        self.results_label.pack(pady=10)

        # Plots Frame (for the graphs)
        self.plots_frame = tk.Frame(self.query_tab, bg=THEME["bg"])
        self.plots_frame.pack(pady=20, fill="both", expand=True)

        self.plot_label = tk.Label(self.plots_frame, text="Plots will appear here", font=("Segoe UI", 14), bg=THEME["bg"], fg=THEME["fg"])
        self.plot_label.pack(pady=10)

        # Profile Tab Content
        self.profile_label = tk.Label(self.profile_tab, text="Profile Information", font=("Segoe UI", 16, "bold"), bg=THEME["bg"], fg=THEME["fg"])
        self.profile_label.pack(pady=20)

        # Placeholder Profile Info
        self.profile_info = tk.Label(self.profile_tab, text="Name: John Doe\nNickname: johndoe123\nEmail: johndoe@email.com", font=("Segoe UI", 14), bg=THEME["bg"], fg=THEME["fg"])
        self.profile_info.pack(pady=10)

    def start_connection_watcher(self):
        def handle_disconnect():
            self.controller.after(0, self.logout_due_to_disconnect)

        threading.Thread(target=ClientConnection.listen_to_server, args=(handle_disconnect,), daemon=True).start()

    def logout_due_to_disconnect(self):
        from Client.gui.login import LoginFrame
        messagebox.showerror("Disconnected", "Server disconnected. Logging out...")
        self.controller.show_frame(LoginFrame)

    # TODO: Implement the functions to handle search queries
    def show_age_distribution(self):
        # Placeholder for the actual function
        print("Showing Age Distribution Plot")
        self.results_label.config(text="Age distribution results will be shown here.")
        self.plot_label.config(text="Age distribution plot will appear here.")

    def show_common_crime(self):
        # Placeholder for the actual function
        print("Showing Most Common Crime")
        self.results_label.config(text="Most common crime results will be shown here.")
        self.plot_label.config(text="Plot for common crime will appear here.")

def start_app_gui(root , connection):
    app = AppGUI(root, None , connection)
    root.mainloop()

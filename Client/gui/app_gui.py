import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from tkinter import Label
import io
import base64


from Client.logic.initial_plots import fetch_initial_plots
from shared.theme import THEME

class AppGUI(tk.Frame):
    def __init__(self, parent, controller, connection, user):
        super().__init__(parent, bg=THEME["bg"])
        self.controller = controller
        self.connection = connection
        self.logged_in_user = user
        self.plot_images = []

        self.pack(fill="both", expand=True)
        toplevel = self.winfo_toplevel()
        toplevel.geometry("1000x700")

        self.tab_control = ttk.Notebook(self)
        self.home_tab = tk.Frame(self.tab_control, bg=THEME["bg"])
        self.query_tab = tk.Frame(self.tab_control, bg=THEME["bg"])
        self.profile_tab = tk.Frame(self.tab_control, bg=THEME["bg"])

        self.tab_control.add(self.home_tab, text="Home")
        self.tab_control.add(self.query_tab, text="Search Queries")
        self.tab_control.add(self.profile_tab, text="Profile")
        self.tab_control.pack(expand=1, fill="both")

        self.setup_home_tab()
        self.setup_query_tab()
        self.setup_profile_tab()
        self.load_initial_plots()
        self.start_connection_watcher()

    def setup_home_tab(self):
        self.home_label = tk.Label(
            self.home_tab, 
            text=f"Welcome to the Client App {self.logged_in_user.nickname}",
            font=("Segoe UI", 22, "bold"), bg=THEME["bg"], fg=THEME["accent"]
        )
        self.home_label.pack(pady=(30, 10))

        # Modern grid container for plots
        self.plot_grid = tk.Frame(self.home_tab, bg=THEME["bg"])
        self.plot_grid.pack(expand=True, fill="both", padx=40, pady=20)

        # Configure grid for 2x2 layout
        for i in range(2):
            self.plot_grid.columnconfigure(i, weight=1, uniform="col")
            self.plot_grid.rowconfigure(i, weight=1, uniform="row")

        # Placeholder for plot cards
        self.plot_cards = []

    def setup_query_tab(self):
        self.query_container = tk.Frame(self.query_tab, bg=THEME["card_bg"])
        self.query_container.place(relx=0.5, rely=0.05, relwidth=0.9, relheight=0.85, anchor="n")

        title_label = tk.Label(self.query_container, text="Search Queries", font=("Segoe UI", 20, "bold"), bg=THEME["card_bg"], fg=THEME["fg"])
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10))

        def add_labeled_entry(row, label_text):
            label = tk.Label(self.query_container, text=label_text, bg=THEME["card_bg"], fg=THEME["fg"], font=("Segoe UI", 12))
            entry = tk.Entry(self.query_container, bg=THEME["entry_bg"], fg=THEME["fg"], insertbackground=THEME["fg"], font=("Segoe UI", 12))
            label.grid(row=row, column=0, padx=20, pady=10, sticky="e")
            entry.grid(row=row, column=1, padx=20, pady=10, sticky="we")
            return entry

        self.time_period_entry = add_labeled_entry(1, "Time Period (e.g. 'month', 'week'):")
        self.area_entry = add_labeled_entry(2, "Area ID:")

        self.age_distribution_button = tk.Button(self.query_container, text="Show Age Distribution", font=("Segoe UI", 11), bg=THEME["button_bg"], fg=THEME["button_fg"], command=self.show_age_distribution)
        self.age_distribution_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.crime_button = tk.Button(self.query_container, text="Show Most Common Crime", font=("Segoe UI", 11), bg=THEME["button_bg"], fg=THEME["button_fg"], command=self.show_common_crime)
        self.crime_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.results_label = tk.Label(self.query_container, text="Results will appear here", font=("Segoe UI", 12, "italic"), bg=THEME["card_bg"], fg=THEME["fg"])
        self.results_label.grid(row=5, column=0, columnspan=2, pady=(20, 5))

        self.plot_label = tk.Label(self.query_container, text="Plots will appear here", font=("Segoe UI", 12, "italic"), bg=THEME["card_bg"], fg=THEME["fg"])
        self.plot_label.grid(row=6, column=0, columnspan=2, pady=(5, 20))

        self.query_container.columnconfigure(1, weight=1)

    def setup_profile_tab(self):
        self.profile_label = tk.Label(self.profile_tab, text="Profile Information", font=("Segoe UI", 16, "bold"), bg=THEME["bg"], fg=THEME["fg"])
        self.profile_label.pack(pady=20)

        self.profile_info = tk.Label(
            self.profile_tab,
            text=f"Name: {self.logged_in_user.name}\nNickname: {self.logged_in_user.nickname}\nEmail: {self.logged_in_user.email}",
            font=("Segoe UI", 14),
            bg=THEME["bg"],
            fg=THEME["fg"]
        )
        self.profile_info.pack(pady=10)

    def load_initial_plots(self):
        """Load and display initial plots in the Home tab."""
        try:
            image_paths = fetch_initial_plots(self.connection)
            plot_titles = [
                "Histogram of Age",
                "Arrests Over Time (Monthly)",
                "Arrests by Gender",
                "Boxplot of Age by Descent Code"
            ]

            # Remove old cards if any
            for card in getattr(self, "plot_cards", []):
                card.destroy()
            self.plot_cards = []

            for idx, (image_path, title) in enumerate(zip(image_paths, plot_titles)):
                row, col = divmod(idx, 2)
                # Card frame
                card = tk.Frame(
                    self.plot_grid,
                    bg=THEME["card_bg"],
                    highlightbackground="#444",
                    highlightthickness=2,
                    bd=0,
                    relief="ridge"
                )
                card.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
                self.plot_cards.append(card)

                # Title
                title_label = tk.Label(
                    card,
                    text=title,
                    font=("Segoe UI", 14, "bold"),
                    bg=THEME["card_bg"],
                    fg=THEME["accent"]
                )
                title_label.pack(pady=(12, 6))

                # Image
                img = Image.open(image_path)
                img = img.resize((340, 220), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                img_label = tk.Label(card, image=img_tk, bg=THEME["card_bg"])
                img_label.image = img_tk  # Keep reference
                img_label.pack(padx=10, pady=(0, 12))

        except Exception as e:
            print(f"[ERROR] Failed to load initial plots: {e}")

    def start_connection_watcher(self):
        """Ensure we are only starting the listener once and handle disconnects properly."""

            # Only start the listener if it's not already running
        if self.connection.listener_thread is None or not self.connection.listener_thread.is_alive():
            threading.Thread(target=self.connection.listen_to_server, args=(self.handle_disconnect,), daemon=True).start()

    def handle_disconnect(self):
        # This method will be called when the server disconnects
            if self.controller:
                self.controller.after(0, self.logout_due_to_disconnect)
            else:
                self.after(0, self.logout_due_to_disconnect)  # Use self if controller is None
    def logout_due_to_disconnect(self):
        """Handle logout due to server disconnection by closing the application."""
        messagebox.showerror("Disconnected", "Server disconnected. The application will now close.")
        if self.controller:
            self.controller.destroy()  # Close the entire application
        else:
            self.quit()  # Fallback to quit if controller is not available
        # Explicitly terminate the program
        import sys
        sys.exit(0)

    def show_age_distribution(self):
        self.results_label.config(text="Age distribution results will be shown here.")
        self.plot_label.config(text="Age distribution plot will appear here.")

    def show_common_crime(self):
        self.results_label.config(text="Most common crime results will be shown here.")
        self.plot_label.config(text="Plot for common crime will appear here.")

def start_app_gui(root, connection, user):
    app = AppGUI(root, root, connection, user)
    root.mainloop()

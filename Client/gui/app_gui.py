import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
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
        toplevel.geometry("1200x800")

        # Modern, wide navigation tabs
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=THEME["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 14, "bold"), padding=[30, 15], background=THEME["card_bg"], foreground=THEME["fg"])
        style.map("TNotebook.Tab", background=[("selected", THEME["accent"])], foreground=[("selected", THEME["button_fg"])])

        self.tab_control = ttk.Notebook(self, style="TNotebook")
        self.home_tab = tk.Frame(self.tab_control, bg=THEME["bg"])
        self.query_tab = tk.Frame(self.tab_control, bg=THEME["bg"])
        self.profile_tab = tk.Frame(self.tab_control, bg=THEME["bg"])

        self.tab_control.add(self.home_tab, text="Home")
        self.tab_control.add(self.query_tab, text="Search Queries")
        self.tab_control.add(self.profile_tab, text="Profile")
        self.tab_control.pack(expand=1, fill="both", padx=0, pady=0, ipadx=0, ipady=0)

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

        for i in range(2):
            self.plot_grid.columnconfigure(i, weight=1, uniform="col")
            self.plot_grid.rowconfigure(i, weight=1, uniform="row")

        self.plot_cards = []

    def setup_query_tab(self):
        # Full-width, modern card container
        self.query_container = tk.Frame(self.query_tab, bg=THEME["card_bg"], bd=0, highlightthickness=0)
        self.query_container.pack(expand=True, fill="both", padx=40, pady=30)

        title_label = tk.Label(
            self.query_container, text="Search Queries", 
            font=("Segoe UI", 24, "bold"), bg=THEME["card_bg"], fg=THEME["accent"]
        )
        title_label.pack(pady=(20, 10), anchor="w")

        # Modern grid for queries
        self.queries_frame = tk.Frame(self.query_container, bg=THEME["card_bg"])
        self.queries_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Query 1: Arrests per time period
        q1_frame = self._make_query_card(
            "Aantal arrestaties per tijdsperiode",
            "Kies tijdsperiode (bijv. 'maand', 'week'):",
            "Show Arrests per Time Period",
            self.query_arrests_per_time_period
        )
        q1_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Query 2: Arrests per area
        q2_frame = self._make_query_card(
            "Arrestaties per gebied",
            "Geef Area ID op:",
            "Show Arrests per Area",
            self.query_arrests_per_area
        )
        q2_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Query 3: Leeftijdsverdeling (with plot)
        q3_frame = self._make_query_card(
            "Leeftijdsverdeling van arrestaties",
            "Geef optioneel een filter op:",
            "Show Age Distribution (with Plot)",
            self.query_age_distribution
        )
        q3_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        # Query 4: Meest voorkomende misdrijfomschrijving
        q4_frame = self._make_query_card(
            "Meest voorkomende misdrijfomschrijving",
            "Geef optioneel een filter op:",
            "Show Most Common Crime",
            self.query_most_common_crime
        )
        q4_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

        self.queries_frame.columnconfigure((0, 1), weight=1)
        self.queries_frame.rowconfigure((0, 1), weight=1)

        # Results area
        self.results_label = tk.Label(
            self.query_container, text="Results will appear here.",
            font=("Segoe UI", 13, "italic"), bg=THEME["card_bg"], fg=THEME["fg"], anchor="w", justify="left"
        )
        self.results_label.pack(fill="x", padx=20, pady=(10, 0))

        self.plot_label = tk.Label(
            self.query_container, text="Plots will appear here.",
            font=("Segoe UI", 13, "italic"), bg=THEME["card_bg"], fg=THEME["fg"], anchor="w", justify="left"
        )
        self.plot_label.pack(fill="x", padx=20, pady=(0, 20))

    def _make_query_card(self, title, entry_label, button_text, command):
        card = tk.Frame(self.queries_frame, bg=THEME["bg"], bd=0, highlightbackground="#444", highlightthickness=2, relief="ridge")
        card.grid_propagate(False)
        card.columnconfigure(0, weight=1)
        card.rowconfigure(2, weight=1)

        title_label = tk.Label(card, text=title, font=("Segoe UI", 16, "bold"), bg=THEME["bg"], fg=THEME["accent"])
        title_label.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        entry = tk.Entry(card, bg=THEME["entry_bg"], fg=THEME["fg"], insertbackground=THEME["fg"], font=THEME["font"], width=30, relief="flat")
        entry.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

        button = tk.Button(card, text=button_text, font=("Segoe UI", 12, "bold"), bg=THEME["button_bg"], fg=THEME["button_fg"], activebackground=THEME["accent_hover"], activeforeground=THEME["fg"], relief="flat", command=lambda: command(entry.get()))
        button.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))

        return card

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

            for card in getattr(self, "plot_cards", []):
                card.destroy()
            self.plot_cards = []

            for idx, (image_path, title) in enumerate(zip(image_paths, plot_titles)):
                row, col = divmod(idx, 2)
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

                title_label = tk.Label(
                    card,
                    text=title,
                    font=("Segoe UI", 14, "bold"),
                    bg=THEME["card_bg"],
                    fg=THEME["accent"]
                )
                title_label.pack(pady=(12, 6))

                img = Image.open(image_path)
                # Use modern Pillow resizing
                resample = getattr(Image, "Resampling", Image).LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
                img = img.resize((340, 220), resample)
                img_tk = ImageTk.PhotoImage(img)
                img_label = tk.Label(card, image=img_tk, bg=THEME["card_bg"])
                img_label.image = img_tk
                img_label.pack(padx=10, pady=(0, 12))

        except Exception as e:
            print(f"[ERROR] Failed to load initial plots: {e}")

    def start_connection_watcher(self):
        if self.connection.listener_thread is None or not self.connection.listener_thread.is_alive():
            threading.Thread(target=self.connection.listen_to_server, args=(self.handle_disconnect,), daemon=True).start()

    def handle_disconnect(self):
        if self.controller:
            self.controller.after(0, self.logout_due_to_disconnect)
        else:
            self.after(0, self.logout_due_to_disconnect)

    def logout_due_to_disconnect(self):
        messagebox.showerror("Disconnected", "Server disconnected. The application will now close.")
        if self.controller:
            self.controller.destroy()
        else:
            self.quit()
        import sys
        sys.exit(0)

    # --- Query Handlers ---

    def query_arrests_per_time_period(self, period):
        # TODO: Implement server call and result display
        self.results_label.config(text=f"Arrest count for period '{period}' will be shown here.")
        self.plot_label.config(text="")

    def query_arrests_per_area(self, area_id):
        # TODO: Implement server call and result display
        self.results_label.config(text=f"Arrest count for area '{area_id}' will be shown here.")
        self.plot_label.config(text="")

    def query_age_distribution(self, filter_value):
        # TODO: Implement server call and result display
        self.results_label.config(text=f"Age distribution (with plot) for filter '{filter_value}' will be shown here.")
        self.plot_label.config(text="")

    def query_most_common_crime(self, filter_value):
        # TODO: Implement server call and result display
        self.results_label.config(text=f"Most common crime for filter '{filter_value}' will be shown here.")
        self.plot_label.config(text="")

def start_app_gui(root, connection, user):
    app = AppGUI(root, root, connection, user)
    root.mainloop()

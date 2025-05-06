import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from Client.logic.initial_plots import fetch_initial_plots
from Client.logic.queries import (
    query_arrests_by_time_period,
    query_arrests_by_area,
    query_age_distribution,
    query_most_common_crime
)
from shared.theme import THEME

class AppGUI(tk.Frame):
    def __init__(self, parent, controller, connection, user):
        super().__init__(parent, bg=THEME["bg"])
        self.controller = controller
        self.connection = connection
        self.logged_in_user = user

        self.pack(fill="both", expand=True)
        toplevel = self.winfo_toplevel()
        toplevel.geometry("1000x600")

        # Modern, wide navigation tabs
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=THEME["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 16, "bold"), padding=[40, 20], background=THEME["card_bg"], foreground=THEME["fg"])
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
        # Main container: left nav + right plot
        self.home_main = tk.Frame(self.home_tab, bg=THEME["bg"])
        self.home_main.pack(expand=True, fill="both", padx=0, pady=0)

        # Vertical navigation bar (links, gecentreerd)
        self.plot_nav = tk.Frame(
            self.home_main,
            bg=THEME["bg"]
        )
        self.plot_nav.pack(side="left", fill="y", padx=(0, 0), pady=0, anchor="w", expand=False)

        # Spacer om verticaal te centreren
        self.plot_nav.grid_rowconfigure(0, weight=1)
        self.plot_nav.grid_rowconfigure(2, weight=1)

        nav_inner = tk.Frame(self.plot_nav, bg=THEME["bg"])
        nav_inner.grid(row=1, column=0, sticky="ns")

        nav_label = tk.Label(
            nav_inner,
            text="Plots",
            font=("Segoe UI", 18, "bold"),
            bg=THEME["bg"],
            fg=THEME["accent"]
        )
        nav_label.pack(pady=(10, 20))

        self.plot_names = [
            "Leeftijdsverdeling van arrestaties",
            "Arrestaties per maand",
            "Arrestaties per geslacht",
            "Top 5 gebieden met meeste arrestaties",
            "Top 5 meest voorkomende misdrijven"
        ]
        self.plot_buttons = []
        for idx, name in enumerate(self.plot_names):
            btn = tk.Label(
                nav_inner,
                text=name,
                font=("Segoe UI", 13),
                bg=THEME["card_bg"],
                fg=THEME["fg"],
                width=28,
                height=2,
                bd=0,
                relief="flat",
                anchor="w",
                padx=18,
                pady=2,
                highlightthickness=2,
                highlightbackground=THEME["bg"],
                highlightcolor=THEME["accent"]
            )
            btn.pack(fill="x", pady=(0, 8))
            btn.bind("<Button-1>", lambda e, i=idx: self.show_plot(i))
            self.plot_buttons.append(btn)

        # Plot display rechts
        self.plot_display = tk.Frame(self.home_main, bg=THEME["card_bg"], bd=0, relief="ridge")
        self.plot_display.pack(side="left", expand=True, fill="both", padx=(40, 0), pady=40)

        self.plot_title_label = tk.Label(
            self.plot_display,
            text="",
            font=("Segoe UI", 18, "bold"),
            bg=THEME["card_bg"],
            fg=THEME["accent"]
        )
        self.plot_title_label.pack(pady=(30, 10))

        self.plot_img_label = tk.Label(self.plot_display, bg=THEME["card_bg"])
        self.plot_img_label.pack(padx=20, pady=10, expand=True)

        self.plot_summary_label = tk.Label(
            self.plot_display,
            text="",
            font=("Segoe UI", 13),
            bg=THEME["card_bg"],
            fg=THEME["fg"],
            anchor="w",
            justify="left"
        )
        self.plot_summary_label.pack(padx=20, pady=(0, 20), anchor="w")

    def setup_query_tab(self):
        # Top bar with tabs (Comparison, Prediction, Overview, Equipment)
        tab_bar = tk.Frame(self.query_tab, bg=THEME["bg"])
        tab_bar.pack(fill="x", pady=(10, 0), padx=0)

        tab_names = [
            "Aantal arrestaties per tijdsperiode",
            "Arrestaties per gebied",
            "Leeftijdsverdeling (grafiek)",
            "Meest voorkomende misdrijf"
        ]
        self.query_tab_buttons = []
        self.active_query_tab = tk.IntVar(value=0)

        for idx, name in enumerate(tab_names):
            btn = tk.Label(
                tab_bar,
                text=name,
                font=("Segoe UI", 12, "bold"),
                bg=THEME["accent"] if idx == 0 else THEME["card_bg"],
                fg=THEME["button_fg"] if idx == 0 else THEME["fg"],
                padx=10, pady=8,
                bd=0,
                relief="flat",
                cursor="hand2"
            )
            btn.pack(side="left", padx=(0, 8))
            btn.bind("<Button-1>", lambda e, i=idx: self.switch_query_tab(i))
            self.query_tab_buttons.append(btn)

        # Main card
        self.query_main_card = tk.Frame(self.query_tab, bg=THEME["card_bg"], bd=0, relief="flat")
        self.query_main_card.pack(expand=True, fill="both", padx=40, pady=(20, 30))

        self.query_info_label = tk.Label(
            self.query_main_card,
            text="",
            font=("Segoe UI", 15, "bold"),
            bg=THEME["card_bg"],
            fg=THEME["fg"],
            anchor="w",
            justify="left"
        )
        self.query_info_label.pack(fill="x", padx=30, pady=(20, 10), anchor="w")

        # Dynamic content frame
        self.query_content_frame = tk.Frame(self.query_main_card, bg=THEME["card_bg"])
        self.query_content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Result card
        self.query_result_card = tk.Frame(self.query_main_card, bg=THEME["entry_bg"], bd=0, relief="flat")
        self.query_result_card.pack(fill="x", padx=20, pady=(0, 20))

        self.query_result_label = tk.Label(
            self.query_result_card,
            text="Result will appear here.",
            font=("Segoe UI", 13),
            bg=THEME["entry_bg"],
            fg=THEME["fg"],
            anchor="w",
            justify="left",
            wraplength=700
        )
        self.query_result_label.pack(fill="x", padx=20, pady=16, anchor="w")

        self.query_plot_label = tk.Label(self.query_result_card, bg=THEME["entry_bg"])
        self.query_plot_label.pack(padx=20, pady=(0, 16))

        self.switch_query_tab(0)  # Show first tab by default

    def switch_query_tab(self, idx):
        # Update tab styles
        for i, btn in enumerate(self.query_tab_buttons):
            if i == idx:
                btn.config(bg=THEME["accent"], fg=THEME["button_fg"])
            else:
                btn.config(bg=THEME["card_bg"], fg=THEME["fg"])

        # Clear previous content
        for widget in self.query_content_frame.winfo_children():
            widget.destroy()
        self.query_result_label.config(text="Result will appear here.")
        self.query_plot_label.config(image="")

        # Query 1: Aantal arrestaties per tijdsperiode
        if idx == 0:
            self.query_info_label.config(text="Aantal arrestaties per tijdsperiode")
            tk.Label(self.query_content_frame, text="Tijdsperiode (bijv. maand, week):", font=THEME["font"], bg=THEME["card_bg"], fg=THEME["fg"]).pack(side="left", padx=(0, 10))
            period_entry = tk.Entry(self.query_content_frame, bg=THEME["entry_bg"], fg=THEME["fg"], insertbackground=THEME["fg"], font=THEME["font"], width=20, relief="flat")
            period_entry.pack(side="left", padx=(0, 10))
            btn = tk.Button(self.query_content_frame, text="Zoek", font=("Segoe UI", 12, "bold"), bg=THEME["button_bg"], fg=THEME["button_fg"], activebackground=THEME["accent_hover"], activeforeground=THEME["fg"], relief="flat", command=lambda: self.query_arrests_per_time_period(period_entry.get()))
            btn.pack(side="left")

        # Query 2: Arrestaties per gebied
        elif idx == 1:
            self.query_info_label.config(text="Arrestaties per gebied")
            tk.Label(self.query_content_frame, text="Area ID:", font=THEME["font"], bg=THEME["card_bg"], fg=THEME["fg"]).pack(side="left", padx=(0, 10))
            area_entry = tk.Entry(self.query_content_frame, bg=THEME["entry_bg"], fg=THEME["fg"], insertbackground=THEME["fg"], font=THEME["font"], width=20, relief="flat")
            area_entry.pack(side="left", padx=(0, 10))
            btn = tk.Button(self.query_content_frame, text="Zoek", font=("Segoe UI", 12, "bold"), bg=THEME["button_bg"], fg=THEME["button_fg"], activebackground=THEME["accent_hover"], activeforeground=THEME["fg"], relief="flat", command=lambda: self.query_arrests_per_area(area_entry.get()))
            btn.pack(side="left")

        # Query 3: Leeftijdsverdeling van arrestaties, met grafiek
        elif idx == 2:
            self.query_info_label.config(text="Leeftijdsverdeling van arrestaties (met grafiek)")
            btn = tk.Button(self.query_content_frame, text="Genereer grafiek", font=("Segoe UI", 12, "bold"), bg=THEME["button_bg"], fg=THEME["button_fg"], activebackground=THEME["accent_hover"], activeforeground=THEME["fg"], relief="flat", command=self.query_age_distribution)
            btn.pack(side="left", padx=(0, 10))

        # Query 4: Meest voorkomende misdrijfomschrijving
        elif idx == 3:
            self.query_info_label.config(text="Meest voorkomende misdrijfomschrijving")
            tk.Label(self.query_content_frame, text="Optioneel filter:", font=THEME["font"], bg=THEME["card_bg"], fg=THEME["fg"]).pack(side="left", padx=(0, 10))
            filter_entry = tk.Entry(self.query_content_frame, bg=THEME["entry_bg"], fg=THEME["fg"], insertbackground=THEME["fg"], font=THEME["font"], width=20, relief="flat")
            filter_entry.pack(side="left", padx=(0, 10))
            btn = tk.Button(self.query_content_frame, text="Zoek", font=("Segoe UI", 12, "bold"), bg=THEME["button_bg"], fg=THEME["button_fg"], activebackground=THEME["accent_hover"], activeforeground=THEME["fg"], relief="flat", command=lambda: self.query_most_common_crime(filter_entry.get()))
            btn.pack(side="left")

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
            summary, image_paths = fetch_initial_plots(self.connection)
            self.plot_images = []
            self.plot_summaries = []

            # Prepare summaries for each plot (customize as needed)
            summaries = [
                f"Totaal aantal arrestaties: {summary.get('total_arrests', '-')}",
                f"Periode: {summary.get('date_range', '-')}",
                f"Geslachten: {', '.join(str(x) for x in summary.get('genders', [])) if summary else '-'}",
                f"Top gebieden: {summary.get('top_areas', '-') if summary else '-'}",
                f"Meest voorkomende misdrijf: {summary.get('top_crime', '-')} ({summary.get('top_crime_count', '-')})"
            ]

            from PIL import Image, ImageTk
            for path in image_paths:
                img = Image.open(path)
                resample = getattr(Image, "Resampling", Image).LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
                img = img.resize((600, 350), resample)
                img_tk = ImageTk.PhotoImage(img)
                self.plot_images.append(img_tk)
            self.plot_summaries = summaries

            self.show_plot(0)  # Show the first plot by default

        except Exception as e:
            print(f"[ERROR] Failed to load initial plots: {e}")

    def show_plot(self, idx):
        self.current_plot_idx = idx
        self.plot_title_label.config(text=self.plot_names[idx])
        self.plot_img_label.config(image=self.plot_images[idx])
        self.plot_img_label.image = self.plot_images[idx]
        self.plot_summary_label.config(text=self.plot_summaries[idx])
        # Highlight selected button
        for i, btn in enumerate(self.plot_buttons):
            if i == idx:
                btn.config(
                    bg=THEME["accent"],
                    fg=THEME["button_fg"],
                    highlightbackground=THEME["accent"],
                    highlightcolor=THEME["accent"]
                )
            else:
                btn.config(
                    bg=THEME["card_bg"],
                    fg=THEME["fg"],
                    highlightbackground=THEME["bg"],
                    highlightcolor=THEME["bg"]
                )

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
        result = query_arrests_by_time_period(self.connection, period)
        if "error" in result:
            self.query_result_label.config(text=f"Error: {result['error']}")
        else:
            data = result["data"]
            result_text = "\n".join([f"{key}: {value}" for key, value in data.items()])
            self.query_result_label.config(text=f"Arrests by {period}:\n{result_text}")

    def query_arrests_per_area(self, area_id):
        result = query_arrests_by_area(self.connection, area_id)
        if "error" in result:
            self.query_result_label.config(text=f"Error: {result['error']}")
        else:
            self.query_result_label.config(text=f"Arrests in area {area_id}: {result['arrests']}")

    def query_age_distribution(self):
        result = query_age_distribution(self.connection)
        if "error" in result:
            self.query_result_label.config(text=f"Error: {result['error']}")
        else:
            bins = result["bins"]
            counts = result["counts"]
            self.query_result_label.config(text="Age distribution plot below:")
            self.display_plot(bins, counts, "Age Distribution", "Age", "Count")

    def query_most_common_crime(self, filter_value):
        result = query_most_common_crime(self.connection, filter_value)
        if "error" in result:
            self.query_result_label.config(text=f"Error: {result['error']}")
        else:
            self.query_result_label.config(text=f"Most common crime: {result['crime']} ({result['count']})")

    def display_plot(self, bins, counts, title, xlabel, ylabel):
        try:
            import matplotlib.pyplot as plt
            from io import BytesIO
            from PIL import Image, ImageTk

            plt.figure(figsize=(6, 4))
            plt.bar(bins, counts, color=THEME["accent"], edgecolor=THEME["fg"])
            plt.title(title, fontsize=14, color=THEME["accent"])
            plt.xlabel(xlabel, fontsize=12, color=THEME["fg"])
            plt.ylabel(ylabel, fontsize=12, color=THEME["fg"])
            plt.xticks(color=THEME["fg"])
            plt.yticks(color=THEME["fg"])
            plt.tight_layout()

            buffer = BytesIO()
            plt.savefig(buffer, format="png", facecolor=THEME["bg"])
            buffer.seek(0)
            img = Image.open(buffer)
            img_tk = ImageTk.PhotoImage(img)
            self.query_plot_label.config(image=img_tk)
            self.query_plot_label.image = img_tk
            buffer.close()
            plt.close()
        except Exception as e:
            self.query_result_label.config(text=f"Error displaying plot: {e}")

def start_app_gui(root, connection, user):
    app = AppGUI(root, root, connection, user)
    root.mainloop()

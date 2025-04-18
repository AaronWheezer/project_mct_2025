import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import io
import base64

from Client.logic.communication import ClientConnection
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

    def setup_home_tab(self):
        self.home_label = tk.Label(
            self.home_tab, 
            text=f"Welcome to the Client App {self.logged_in_user.nickname}",
            font=("Segoe UI", 18, "bold"), bg=THEME["bg"], fg=THEME["fg"]
        )
        self.home_label.pack(pady=20)

        self.plot_container = tk.Frame(self.home_tab, bg=THEME["bg"])
        self.plot_container.pack(pady=10)

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
        def task():
            encoded_plots = fetch_initial_plots(self.connection)
            if not encoded_plots:
                return

            # Clear the previous plot images
            for widget in self.plot_container.winfo_children():
                widget.destroy()

            self.plot_images.clear()

            for encoded_image in encoded_plots:
                try:
                    image_data = base64.b64decode(encoded_image)
                    image = Image.open(io.BytesIO(image_data)).resize((400, 300))
                    photo = ImageTk.PhotoImage(image)
                    label = tk.Label(self.plot_container, image=photo, bg=THEME["bg"])
                    label.image = photo  
                    label.pack(side="left", padx=10)
                    self.plot_images.append(photo)

                except Exception as e:
                    print(f"[ERROR] Failed to load image: {e}")

        threading.Thread(target=task, daemon=True).start()

    def start_connection_watcher(self):
        def handle_disconnect():
            self.controller.after(0, self.logout_due_to_disconnect)

        threading.Thread(target=ClientConnection.listen_to_server, args=(handle_disconnect,), daemon=True).start()

    def logout_due_to_disconnect(self):
        from Client.gui.login import LoginFrame
        messagebox.showerror("Disconnected", "Server disconnected. Logging out...")
        self.controller.show_frame(LoginFrame)

    def show_age_distribution(self):
        self.results_label.config(text="Age distribution results will be shown here.")
        self.plot_label.config(text="Age distribution plot will appear here.")

    def show_common_crime(self):
        self.results_label.config(text="Most common crime results will be shown here.")
        self.plot_label.config(text="Plot for common crime will appear here.")

def start_app_gui(root, connection, user):
    app = AppGUI(root, None, connection, user)
    root.mainloop()

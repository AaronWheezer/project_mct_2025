# Client/gui/main_window.py

import tkinter as tk
from Client.gui.login import LoginFrame
from Client.gui.register import RegisterFrame
import Client.gui.frames as frames
from Client.gui.frames import AppController

def start_gui():
    root = tk.Tk()
    app = AppController(root)

    # Let Tkinter figure out the best size
    root.update()  # Force geometry calculation
    width = app.winfo_width()
    height = app.winfo_height()

    root.geometry(f"{width}x{height}+200+100")  # Position it nicely on screen
    root.resizable(False, False)  # Optional: prevent resizing

    root.mainloop()
# Client/gui/main_window.py

import tkinter as tk
from Client.gui.login import LoginFrame
from Client.gui.register import RegisterFrame
import Client.gui.frames as frames
from Client.gui.frames import AppController
class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Arrest App")
        self.root.geometry("300x300")

        # Set the actual class references
        frames.LoginFrame = LoginFrame
        frames.RegisterFrame = RegisterFrame

        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (LoginFrame, RegisterFrame):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginFrame)

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()

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
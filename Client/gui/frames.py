import tkinter as tk
from Client.gui.login import LoginFrame
from Client.gui.register import RegisterFrame

class AppController(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.pack(fill="both", expand=True)

        self.frames = {}

        for F in (LoginFrame, RegisterFrame):
            frame = F(self, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginFrame)

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()

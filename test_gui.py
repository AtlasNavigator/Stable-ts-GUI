import customtkinter
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk

try:
    print("Initializing App...")
    class App(customtkinter.CTk, TkinterDnD.DnDWrapper):
        def __init__(self):
            super().__init__()
            print("Super init done")
            self.TkdndVersion = TkinterDnD._require(self)
            print("Tkdnd required")
            
            self.title("Test App")
            self.geometry("400x300")
            
            label = customtkinter.CTkLabel(self, text="Test")
            label.pack()
            
            print("Setup done")

    app = App()
    print("App created")
    app.after(1000, app.destroy) # Close after 1s
    app.mainloop()
    print("Mainloop finished")
except Exception as e:
    print(f"CRASHED: {e}")
    import traceback
    traceback.print_exc()

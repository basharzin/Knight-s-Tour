import tkinter as tk
from src.gui import KnightTourGUI

if __name__ == "__main__":
    root = tk.Tk()
    # Set high resolution support for Windows (Optional)
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
        
    app = KnightTourGUI(root)
    root.mainloop()
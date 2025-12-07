"""
Main Entry Point for the Knight's Tour Solver Application.

This script initializes the Tkinter root window, configures high-DPI scaling
for Windows systems (to ensure sharp text), and launches the main GUI application.
"""

import tkinter as tk
from src.gui import KnightTourGUI

if __name__ == "__main__":
    root = tk.Tk()

    
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        
        pass

    
    app = KnightTourGUI(root)
    root.mainloop()
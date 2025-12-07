import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
import time
import csv
import os
from datetime import datetime

# Import Solvers
from src.backtracking import BacktrackingSolver
from src.cultural import CulturalSolver

class KnightTourGUI:
    """
    Main GUI Class for the Knight's Tour Application.
    Handles user interaction, visualization, and recording of results.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("♟️ Knight's Tour Solver - Group 53")
        self.root.geometry("1150x800")
        
        # Initialize History Data
        self.csv_filename = "knights_tour_results.csv"
        self.history = [] 
        self.initialize_csv() 
        self.load_history_from_csv()
        
        # Styling Setup
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.bg_color = "#ecf0f1"
        self.panel_color = "#2c3e50" 
        self.success_color = "#27ae60" 
        
        self.root.configure(bg=self.bg_color)
        
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("Control.TFrame", background=self.panel_color)
        self.style.configure("TLabel", background=self.panel_color, foreground="white", font=("Segoe UI", 10))
        self.style.configure("Hint.TLabel", background=self.panel_color, foreground="#bdc3c7", font=("Segoe UI", 8))
        self.style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), background=self.panel_color, foreground="#f1c40f")
        
        # ================= Layout =================
        self.sidebar = ttk.Frame(root, style="Control.TFrame", width=340)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        ttk.Label(self.sidebar, text="Knight's Tour", style="Header.TLabel").pack(pady=(30, 5))
        ttk.Label(self.sidebar, text="Auto-Saving & Loading 📂", style="TLabel").pack(pady=(0, 20))

        # --- Board Size Input ---
        f = ttk.Frame(self.sidebar, style="Control.TFrame")
        f.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(f, text="Board Size (N):", style="TLabel").pack(anchor="w")
        
        # Board Size Combobox
        self.combo_n = ttk.Combobox(f, values=[6, 8, 10, 12, 16, 20, 30], font=("Segoe UI", 12, "bold"), state="readonly")
        self.combo_n.current(1) # Default to 8
        self.combo_n.pack(fill=tk.X, pady=2, ipady=8)
        
        ttk.Label(self.sidebar, text="Select from specific sizes", style="Hint.TLabel").pack(anchor="w", padx=20, pady=(0, 10))

        # --- Start Position Inputs ---
        self.create_spinbox("Start Row:", 0, 29, 0)
        self.entry_r = self.last_spinbox
        
        self.create_spinbox("Start Col:", 0, 29, 0)
        self.entry_c = self.last_spinbox
        ttk.Label(self.sidebar, text="Must be < Board Size", style="Hint.TLabel").pack(anchor="w", padx=20, pady=(0, 10))

        # --- Algorithm Selection ---
        ttk.Label(self.sidebar, text="Select Strategy:", style="TLabel", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=20, pady=(20, 10))
        self.algo_var = tk.StringVar(value="Backtracking")
        self.style.configure("TRadiobutton", background=self.panel_color, foreground="white", font=("Segoe UI", 10))
        ttk.Radiobutton(self.sidebar, text="Backtracking (Exact)", variable=self.algo_var, value="Backtracking").pack(anchor="w", padx=25)
        ttk.Radiobutton(self.sidebar, text="Cultural Algorithm (AI)", variable=self.algo_var, value="Cultural").pack(anchor="w", padx=25)

        # --- Action Buttons ---
        btn_frame = ttk.Frame(self.sidebar, style="Control.TFrame")
        btn_frame.pack(fill=tk.X, padx=20, pady=30)
        
        self.run_btn = tk.Button(btn_frame, text="▶ START SIMULATION", bg=self.success_color, fg="white", font=("Segoe UI", 11, "bold"), bd=0, padx=10, pady=10, cursor="hand2", command=self.run_solver)
        self.run_btn.pack(fill=tk.X, pady=5)
        
        self.compare_btn = tk.Button(btn_frame, text="📊 COMPARE LAST TWO", bg="#2980b9", fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=10, pady=8, cursor="hand2", command=self.run_comparison)
        self.compare_btn.pack(fill=tk.X, pady=5)

        self.hist_btn = tk.Button(btn_frame, text="📜 VIEW ALL HISTORY", bg="#f39c12", fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=10, pady=10, cursor="hand2", command=self.view_full_history)
        self.hist_btn.pack(fill=tk.X, pady=10)

        self.clear_btn = tk.Button(btn_frame, text="🗑️ CLEAR HISTORY", bg="#c0392b", fg="white", font=("Segoe UI", 9, "bold"), bd=0, padx=10, pady=5, cursor="hand2", command=self.clear_history)
        self.clear_btn.pack(fill=tk.X, pady=5)

        # --- Status Bar ---
        self.status_var = tk.StringVar(value=f"Loaded {len(self.history)} records.")
        self.status_bar = tk.Label(self.sidebar, textvariable=self.status_var, bg="#1a252f", fg="#f39c12", font=("Consolas", 11, "bold"), pady=15, wraplength=300)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 2. Plot Area
        self.plot_area = ttk.Frame(root, style="TFrame")
        self.plot_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.figure, self.ax = plt.subplots(figsize=(6, 6))
        self.figure.patch.set_facecolor(self.bg_color)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_area)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.ax.axis('off')
        self.canvas.draw()

    # --- CSV HANDLING (LOAD & SAVE) ---
    def initialize_csv(self):
        if not os.path.exists(self.csv_filename):
            try:
                with open(self.csv_filename, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["ID", "Timestamp", "Board", "Algorithm", "Time", "Result", "Success"])
            except Exception as e:
                messagebox.showerror("CSV Error", f"Could not create file: {e}")

    def load_history_from_csv(self):
        if os.path.exists(self.csv_filename):
            try:
                with open(self.csv_filename, mode='r') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        self.history.append(row)
            except Exception as e:
                print(f"Error loading: {e}")

    def create_spinbox(self, label, min_val, max_val, default):
        f = ttk.Frame(self.sidebar, style="Control.TFrame")
        f.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(f, text=label, style="TLabel").pack(anchor="w")
        spin = ttk.Spinbox(f, from_=min_val, to=max_val, font=("Segoe UI", 14, "bold"), width=12)
        spin.set(default)
        spin.pack(fill=tk.X, pady=2, ipady=8) 
        self.last_spinbox = spin

    def get_inputs(self):
        try:
            n = int(self.combo_n.get())
            r = int(self.entry_r.get())
            c = int(self.entry_c.get())
            if not (0 <= r < n and 0 <= c < n): raise ValueError
            return n, r, c
        except:
            messagebox.showerror("Error", "Check inputs! Row/Col must be smaller than Board Size.")
            return None

    def log_result(self, res, n, r, c):
        record = {
            "ID": len(self.history) + 1,
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "Board": f"{n}x{n}",
            "Algorithm": res['algorithm'],
            "Time": f"{res['time']:.4f}s",
            "Result": f"{res['steps']}/{n*n}",
            "Success": "Yes" if res['success'] else "No"
        }
        self.history.append(record)
        try:
            with open(self.csv_filename, mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=record.keys())
                writer.writerow(record)
        except Exception as e:
            print(f"Auto-save failed: {e}")

    # --- View Full History Window ---
    def view_full_history(self):
        if not self.history:
            messagebox.showinfo("Info", "History is empty.")
            return

        win = Toplevel(self.root)
        win.title("📜 Complete Session History")
        win.geometry("750x450")
        
        cols = ("ID", "Timestamp", "Board", "Algorithm", "Time", "Result", "Success")
        tree = ttk.Treeview(win, columns=cols, show='headings')
        
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=95, anchor="center")
        
        for row in self.history:
            tree.insert("", "end", values=(row["ID"], row["Timestamp"], row["Board"], row["Algorithm"], row["Time"], row["Result"], row["Success"]))
            
        scrollbar = ttk.Scrollbar(win, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)

    def clear_history(self):
        if messagebox.askyesno("Confirm", "Delete ALL history logs?"):
            self.history = []
            try:
                with open(self.csv_filename, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["ID", "Timestamp", "Board", "Algorithm", "Time", "Result", "Success"])
                self.status_var.set("History Cleared.")
                messagebox.showinfo("Success", "History cleared.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def draw_board_base(self, n):
        self.ax.clear()
        self.ax.axis('off')
        for r in range(n):
            for c in range(n):
                color = '#f0d9b5' if (r + c) % 2 == 0 else '#b58863'
                rect = patches.Rectangle((c, n - 1 - r), 1, 1, facecolor=color, edgecolor='none')
                self.ax.add_patch(rect)
        self.ax.set_xlim(0, n)
        self.ax.set_ylim(0, n)
        self.canvas.draw()

    def animate_path(self, n, path, algo_name):
        self.draw_board_base(n)
        xs, ys = [], []
        
        # Animation Speed (0.05 = Balanced speed)
        delay = 0.05 
        
        color_line = '#2980b9' if algo_name == "Backtracking" else '#8e44ad'
        total_sq = n * n

        for i, (r, c) in enumerate(path):
            px, py = c + 0.5, n - 1 - r + 0.5
            xs.append(px)
            ys.append(py)

            if i > 0:
                self.ax.plot(xs[-2:], ys[-2:], color=color_line, linewidth=2.5, alpha=0.8)
            
            if hasattr(self, 'knight'): self.knight.remove()
            self.knight = self.ax.text(px, py, '♞', fontsize=26, ha='center', va='center', color='black')
            self.ax.text(px, py, str(i), fontsize=8, ha='center', va='center', color='white', fontweight='bold')
            
            self.status_var.set(f"RUNNING... Steps: {i+1} / {total_sq}")
            
            self.canvas.draw()
            self.root.update()
            
            time.sleep(delay)

        # Draw Start/End Markers
        sr, sc = path[0]
        self.ax.add_patch(patches.Rectangle((sc, n - 1 - sr), 1, 1, facecolor='#2ecc71', alpha=0.5, edgecolor='green', linewidth=3))
        self.ax.text(sc+0.5, n - 1 - sr + 0.5 - 0.35, "START", color='darkgreen', fontsize=9, fontweight='bold', ha='center')

        er, ec = path[-1]
        self.ax.add_patch(patches.Rectangle((ec, n - 1 - er), 1, 1, facecolor='#e74c3c', alpha=0.5, edgecolor='red', linewidth=3))
        self.ax.text(ec+0.5, n - 1 - er + 0.5 - 0.35, "END", color='darkred', fontsize=9, fontweight='bold', ha='center')
        
        self.canvas.draw()
        
        if len(path) == total_sq:
            self.status_var.set(f"✅ COMPLETE! (Saved)")
        else:
            self.status_var.set(f"⚠️ INCOMPLETE (Saved)")

    def run_solver(self):
        vals = self.get_inputs()
        if not vals: return
        n, r, c = vals
        algo = self.algo_var.get()

        self.status_var.set("Processing...")
        self.root.update()

        if algo == "Backtracking":
            res = BacktrackingSolver(n).run(r, c)
        else:
            res = CulturalSolver(n, max_gens=3000).run(r, c)
        
        self.log_result(res, n, r, c)

        if res['success'] or len(res['path']) > 0:
            self.animate_path(n, res['path'], algo)
        else:
            messagebox.showerror("Failed", "No solution found!")
            self.status_var.set("Failed. (Saved)")

    def run_comparison(self):
        vals = self.get_inputs()
        if not vals: return
        n, r, c = vals
        
        self.status_var.set("Benchmarking...")
        self.root.update()

        bt = BacktrackingSolver(n).run(r, c)
        ca = CulturalSolver(n, max_gens=2000).run(r, c)
        
        self.log_result(bt, n, r, c)
        self.log_result(ca, n, r, c)

        win = Toplevel(self.root)
        win.title(f"Comparison Results (N={n})")
        win.geometry("500x350")
        win.configure(bg="white")
        
        tk.Label(win, text="🏆 Last Run Comparison", font=("Segoe UI", 14, "bold"), bg="white", fg="#2c3e50").pack(pady=15)
        f = tk.Frame(win, bg="#f9f9f9", bd=1, relief="solid")
        f.pack(padx=20, pady=10, fill="both", expand=True)

        tk.Label(f, text="Metric", font=("bold"), bg="#ddd", width=15).grid(row=0, column=0)
        tk.Label(f, text="Backtracking", font=("bold"), bg="#3498db", fg="white", width=15).grid(row=0, column=1)
        tk.Label(f, text="Cultural Algo", font=("bold"), bg="#9b59b6", fg="white", width=15).grid(row=0, column=2)

        metrics = [
            ("Time (sec)", f"{bt['time']:.5f}", f"{ca['time']:.5f}"),
            ("Status", "Success ✅" if bt['success'] else "Fail ❌", "Success ✅" if ca['success'] else "Fail ❌"),
            ("Steps", f"{bt['steps']}", f"{ca['steps']}")
        ]

        for i, (m, v1, v2) in enumerate(metrics):
            bg = "white" if i % 2 == 0 else "#f4f4f4"
            tk.Label(f, text=m, bg=bg).grid(row=i+1, column=0, sticky="nsew", ipady=5)
            tk.Label(f, text=v1, bg=bg).grid(row=i+1, column=1, sticky="nsew")
            tk.Label(f, text=v2, bg=bg).grid(row=i+1, column=2, sticky="nsew")
        
        self.status_var.set(f"Comparison Done. Data Saved.")
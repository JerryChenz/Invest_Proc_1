import tkinter as tk
from tkinter import ttk, messagebox
from smart_value.tools import model_update, stock_monitor
from smart_value.tools.model_new import new_stock_model


def update_model(root, status_var):
    try:
        model_update.update_models()
        status_var.set("Update completed successfully")
    except Exception as e:
        messagebox.showerror("Error", f"Model update failed: {str(e)}", parent=root)
        status_var.set("Update failed")


def create_model(root, symbol_var, comp_var, status_var):
    symbol = symbol_var.get().strip()
    comp_group = comp_var.get().strip()

    if not symbol:
        messagebox.showwarning("Input Error", "Stock symbol is required", parent=root)
        return

    try:
        new_stock_model(symbol, comp_group)
        status_var.set(f"Created model for {symbol}")
        messagebox.showinfo("Success", f"Model created for {symbol}", parent=root)
    except Exception as e:
        messagebox.showerror("Error", f"Model creation failed: {str(e)}", parent=root)


def invest_proc():
    root = tk.Tk()
    root.title("SmartValuation Pro v4.0")
    root.geometry("800x400")

    # Coinbase-style color scheme
    coinbase_blue = "#0052FF"
    light_gray = "#F7F9FA"
    white = "#FFFFFF"
    dark_gray = "#3C3F44"
    light_text = "#69737D"

    # Style configuration
    style = ttk.Style()
    style.theme_use('clam')

    # Configure styles to match Coinbase aesthetic
    style.configure('TFrame', background=white)
    style.configure('TLabel', background=white, foreground=dark_gray, font=('Segoe UI', 10))
    style.configure('TButton', background=coinbase_blue, foreground=white, font=('Segoe UI', 10, 'bold'), borderwidth=0,
                    focusthickness=0, focuscolor='')
    style.map('TButton', background=[('active', '!disabled', '#0035CC')])
    style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'), foreground=dark_gray)
    style.configure('Status.TLabel', font=('Segoe UI', 9), foreground=light_text)

    # Create main container
    main_container = ttk.Frame(root, padding=20)
    main_container.pack(fill='both', expand=True)

    # Create frames
    control_frame = ttk.Frame(main_container)
    control_frame.pack(fill='x', pady=(0, 20))

    input_frame = ttk.Frame(main_container)
    input_frame.pack(fill='x', pady=(0, 20))

    status_frame = ttk.Frame(main_container)
    status_frame.pack(fill='x')

    # Create variables
    symbol_var = tk.StringVar()
    comp_var = tk.StringVar()
    status_var = tk.StringVar()
    status_var.set("Ready")

    # Model Operations Section
    ttk.Label(control_frame, text="Model Operations", style='Header.TLabel').grid(row=0, column=0, columnspan=3,
                                                                                  pady=(0, 15), sticky='w')

    ttk.Button(control_frame, text="Update Model",
               command=lambda: update_model(root, status_var)).grid(row=1, column=0, padx=10, pady=5, sticky='ew')
    ttk.Button(control_frame, text="Full Monitor Update",
               command=lambda: stock_monitor.update_monitor(False)).grid(row=1, column=1, padx=10, pady=5, sticky='ew')
    ttk.Button(control_frame, text="Simple Monitor Update",
               command=lambda: stock_monitor.update_monitor(True)).grid(row=1, column=2, padx=10, pady=5, sticky='ew')

    control_frame.columnconfigure((0, 1, 2), weight=1)

    # New Model Creation Section
    ttk.Label(input_frame, text="New Model Creation", style='Header.TLabel').grid(row=0, column=0, columnspan=3,
                                                                                  pady=(0, 15), sticky='w')

    ttk.Label(input_frame, text="Stock Symbol:").grid(row=1, column=0, sticky='w', pady=5)
    ttk.Entry(input_frame, textvariable=symbol_var).grid(row=1, column=1, sticky='ew', pady=5)

    ttk.Label(input_frame, text="Comparison Group:").grid(row=2, column=0, sticky='w', pady=5)
    ttk.Entry(input_frame, textvariable=comp_var).grid(row=2, column=1, sticky='ew', pady=5)

    ttk.Button(input_frame, text="Create Model",
               command=lambda: create_model(root, symbol_var, comp_var, status_var)).grid(row=1, column=2, rowspan=2,
                                                                                          padx=10, pady=5, sticky='ew')

    input_frame.columnconfigure(1, weight=1)

    # Status Bar
    ttk.Label(status_frame, textvariable=status_var, style='Status.TLabel').pack(side='right')

    root.mainloop()

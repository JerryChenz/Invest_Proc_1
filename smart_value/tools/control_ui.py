import tkinter as tk
from tkinter import ttk, messagebox
from smart_value.tools import stock_monitor
from smart_value.tools.update import model_update
from smart_value.tools.model_new import new_stock_model
from smart_value.tools.find_docs import models_folder
from smart_value.tools.level2_screener import update_level2_screener
import os
import subprocess

"""
Invest_Proc - A GUI Application for Financial Analysis Automation

This application provides a user interface to automate various financial analysis tasks including:
1. Updating market screeners for different regions
2. Performing model operations (updating models, monitoring stocks)
3. Creating new financial models for specific stock symbols
4. Quick access to generated model documents

The GUI is organized into four main sections:
- Screener Updates: Buttons to refresh HK, CN, and US market screeners
- Model Operations: Tools for updating models and stock monitors
- New Model Creation: Form to generate new stock models with comparison groups
- Utilities: Status bar and quick access to generated documents

The interface follows Coinbase's visual style with a blue/white color scheme and modern typography.
"""


def update_screener(sheet_name, root, status_var):
    """
    Update the specified screener and reflect the status in the GUI.

    Args:
        sheet_name (str): Name of the screener sheet to update (e.g., 'hk_screener').
        root (tk.Tk): The main Tkinter window instance.
        status_var (tk.StringVar): Variable to display the operation status.
    """
    try:
        update_level2_screener(sheet_name)
        status_var.set(f"{sheet_name} updated successfully")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update {sheet_name}: {str(e)}", parent=root)
        status_var.set(f"Update failed for {sheet_name}")


def update_model(root, status_var):
    """
    Update all existing stock models and update the GUI status.

    Args:
        root (tk.Tk): The main Tkinter window instance.
        status_var (tk.StringVar): Variable to display the operation status.
    """
    try:
        model_update.update_models()
        status_var.set("Update completed successfully")
    except Exception as e:
        messagebox.showerror("Error", f"Model update failed: {str(e)}", parent=root)
        status_var.set("Update failed")


def create_model(root, symbol_var, comp_var, status_var):
    """
    Create a new stock model based on user input and update the GUI status.

    Args:
        root (tk.Tk): The main Tkinter window instance.
        symbol_var (tk.StringVar): Variable containing the stock symbol input.
        comp_var (tk.StringVar): Variable containing the comparison group input.
        status_var (tk.StringVar): Variable to display the operation status.
    """
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
    """
    Launch the Invest_Proc GUI application for stock model management.

    This function initializes a Tkinter window with sections for:
    - Updating regional stock screeners (HK, CN, US)
    - Managing stock models (update existing, full/simple monitor updates)
    - Creating new stock models with symbol and comparison group inputs
    - Opening the models folder in the system file explorer
    The GUI is styled with a Coinbase-inspired design using custom colors and layouts.
    """
    # Initialize the main window
    root = tk.Tk()
    root.title("Invest_Proc")
    root.geometry("800x500")

    # Define color scheme
    coinbase_blue = "#0052FF"
    light_gray = "#F7F9FA"
    white = "#FFFFFF"
    dark_gray = "#3C3F44"
    light_text = "#69737D"

    # Configure ttk styles
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TFrame', background=white)
    style.configure('TLabel', background=white, foreground=dark_gray, font=('Segoe UI', 10))
    style.configure('TButton', background=coinbase_blue, foreground=white, font=('Segoe UI', 10, 'bold'),
                    borderwidth=0, focusthickness=0, focuscolor='')
    style.map('TButton', background=[('active', '!disabled', '#0035CC')])
    style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'), foreground=dark_gray)
    style.configure('Status.TLabel', font=('Segoe UI', 9), foreground=light_text)

    # Main container setup
    main_container = ttk.Frame(root, padding=20)
    main_container.pack(fill='both', expand=True)

    # Create section frames
    control_frame = ttk.Frame(main_container)
    control_frame.pack(fill='x', pady=(0, 20))

    input_frame = ttk.Frame(main_container)
    input_frame.pack(fill='x', pady=(0, 20))

    screener_frame = ttk.Frame(main_container)
    screener_frame.pack(fill='x', pady=(0, 20))

    status_frame = ttk.Frame(main_container)
    status_frame.pack(fill='x')

    # Initialize GUI variables
    symbol_var = tk.StringVar()
    comp_var = tk.StringVar()
    status_var = tk.StringVar(value="Ready")

    # Screener Updates Section
    ttk.Label(screener_frame, text="Screener Updates", style='Header.TLabel').grid(row=0, column=0, columnspan=3,
                                                                                   pady=(0, 15), sticky='w')
    screener_buttons = [
        ('HK Screener', 'hk_screener'),
        ('CN Screener', 'cn_screener'),
        ('US Screener', 'us_screener')
    ]
    for col, (btn_text, sheet_name) in enumerate(screener_buttons):
        ttk.Button(screener_frame, text=f"Update {btn_text}",
                   command=lambda sn=sheet_name: update_screener(sn, root, status_var)).grid(row=1, column=col,
                                                                                             padx=10, pady=5,
                                                                                             sticky='ew')
    screener_frame.columnconfigure((0, 1, 2), weight=1)

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
                                                                                          padx=10, pady=5,
                                                                                          sticky='ew')
    input_frame.columnconfigure(1, weight=1)

    # Status Bar
    ttk.Label(status_frame, textvariable=status_var, style='Status.TLabel').pack(side='right')

    # Open Models Folder Section
    button_frame = ttk.Frame(main_container)
    button_frame.pack(side='bottom', fill='x', pady=10)

    def open_models_folder():
        """
        Open the models folder in the system's default file explorer.
        """
        path = models_folder.resolve()
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(path))
            elif os.name == 'posix':  # Unix-like
                if hasattr(os, 'uname') and os.uname().sysname == 'Darwin':  # macOS
                    subprocess.run(['open', str(path)])
                else:  # Linux
                    subprocess.run(['xdg-open', str(path)])
            else:
                messagebox.showwarning("Unsupported OS", "Opening folders is not supported on this OS.", parent=root)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}", parent=root)

    ttk.Button(button_frame, text="Open Opportunities Folder", command=open_models_folder).pack(expand=True,
                                                                                                anchor='center')

    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    invest_proc()

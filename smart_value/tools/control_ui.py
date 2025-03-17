import tkinter as tk
from smart_value.tools import model_update, stock_monitor
from smart_value.tools.model_new import new_stock_model


def full_update():
    # Step 1: update the xls with the latest template, and market data
    model_update.update_models()
    # Step 2: update the monitor
    # stock_monitor.update_monitor(True)


def invest_proc():
    # Create the main application window
    root = tk.Tk()
    root.title("Invest Proc_v3")

    # Create a button
    full_update_button = tk.Button(root, text="Full Update", command=full_update)
    full_update_button.grid(column=0, row=0)
    full_monitor_button = tk.Button(root, text="Full Monitor Update",
                                    command=lambda: stock_monitor.update_monitor(False))
    full_monitor_button.grid(column=1, row=0)
    simple_monitor_button = tk.Button(root, text="Simple Monitor Update",
                                      command=lambda: stock_monitor.update_monitor(True))
    simple_monitor_button.grid(column=2, row=0)

    # declaring string variable for storing symbol and comp_group
    symbol_var = tk.StringVar()
    comp_var = tk.StringVar()

    # creating a label and an entry for symbol
    symbol_label = tk.Label(root, text='symbol', font=('calibre', 10, 'bold'))
    symbol_entry = tk.Entry(root, textvariable=symbol_var, font=('calibre', 10, 'normal'))

    # creating a label and an entry for comp_group
    comp_label = tk.Label(root, text='comp_group', font=('calibre', 10, 'bold'))
    comp_entry = tk.Entry(root, textvariable=comp_var, font=('calibre', 10, 'normal'))

    # creating a button
    new_btn = tk.Button(root, text='create', command=lambda: new_stock_model(symbol_var.get(), comp_var.get()))

    # placing the label and entry in the required position
    symbol_label.grid(column=0, row=1)
    symbol_entry.grid(column=0, row=2)
    comp_label.grid(column=1, row=1)
    comp_entry.grid(column=1, row=2)
    new_btn.grid(column=2, row=2)

    # Run the application
    root.mainloop()

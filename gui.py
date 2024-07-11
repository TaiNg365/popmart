# gui.py
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import ctypes
import platform
from main import check_product

stop_event = threading.Event()
stop_events = []
threads = []

def set_app_icon():
    try:
        # Use the path to your .ico file
        if platform.system() == 'Windows':
            app_icon = 'labubuicon.ico'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_icon)
            root.iconbitmap(app_icon)
        elif platform.system() == 'Darwin':  # macOS
            root.iconbitmap('@labubuicon.icns')  # Use .icns format for macOS
        else:  # Linux
            root.iconbitmap('@labubuicon.xbm')  # Use .xbm format for Linux
    except Exception as e:
        print(f"Error setting app icon: {e}")

def start_bot():
    global stop_event, threads, stop_events

    # Collect user details from the GUI entries
    card_number = str(card_number_entry.get())
    card_expiry_date = str(card_expiry_entry.get())
    card_security_code = str(security_code_entry.get())
    card_holder_name = str(card_holder_name_entry.get())
    user_email = str(email_entry.get())
    user_password = str(password_entry.get())

    # Ensure all fields are filled
    if not all([card_number, card_expiry_date, card_security_code, card_holder_name, user_email, user_password]):
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    # Parse product list from the entry
    product_list_input = product_list_entry.get().strip().split(',')
    product_list = {}
    for item in product_list_input:
        try:
            product, option, quantity = item.strip().split(':')
            product_list[product.strip()] = (option.strip(), int(quantity.strip()))
        except ValueError:
            messagebox.showerror("Error", "Invalid format for product list. Please use the format 'product:option:quantity' for each product.")
            return

    # Clear the stop event and threads list
    stop_event.clear()
    threads = []

    # Start threads for each product
    for product, (option, quantity) in product_list.items():
        stop_event_local = threading.Event()
        stop_events.append(stop_event_local)
        thread = threading.Thread(target=check_product, args=(product, option, quantity, stop_event_local, user_email, user_password, card_number, card_expiry_date, card_security_code, card_holder_name))
        threads.append(thread)
        thread.start()

    #messagebox.showinfo("Info", "Bot started.")

def stop_bot():
    global stop_events, threads

    for stop_event_local in stop_events:
        stop_event_local.set()
    
    for thread in threads:
        thread.join()

    # # Clear all fields
    # card_number_entry.delete(0, tk.END)
    # card_expiry_entry.delete(0, tk.END)
    # security_code_entry.delete(0, tk.END)
    # card_holder_name_entry.delete(0, tk.END)
    # email_entry.delete(0, tk.END)
    # password_entry.delete(0, tk.END)
    # product_list_entry.delete(0, tk.END)

    stop_events.clear()
    threads.clear()

    messagebox.showinfo("Info", "Bot stopped")

# Create the main application window
root = tk.Tk()
root.title("Checkout Bot")

# Make the window resizable
root.resizable(True, True)

# Set the application icon
set_app_icon()

# Create and place the widgets
tk.Label(root, text="Card Number:").grid(row=0, column=0, sticky="w")
card_number_entry = tk.Entry(root)
card_number_entry.grid(row=0, column=1, sticky="ew")

tk.Label(root, text="Expiry Date (MM/YY):").grid(row=1, column=0, sticky="w")
card_expiry_entry = tk.Entry(root)
card_expiry_entry.grid(row=1, column=1, sticky="ew")

tk.Label(root, text="Security Code:").grid(row=2, column=0, sticky="w")
security_code_entry = tk.Entry(root)
security_code_entry.grid(row=2, column=1, sticky="ew")

tk.Label(root, text="Card Holder Name:").grid(row=3, column=0, sticky="w")
card_holder_name_entry = tk.Entry(root)
card_holder_name_entry.grid(row=3, column=1, sticky="ew")

tk.Label(root, text="Email:").grid(row=4, column=0, sticky="w")
email_entry = tk.Entry(root)
email_entry.grid(row=4, column=1, sticky="ew")

tk.Label(root, text="Password:").grid(row=5, column=0, sticky="w")
password_entry = tk.Entry(root, show="*")
password_entry.grid(row=5, column=1, sticky="ew")

tk.Label(root, text="Product List (product:option:quantity, ...):").grid(row=6, column=0, sticky="w")
product_list_entry = tk.Entry(root)
product_list_entry.grid(row=6, column=1, sticky="ew")

# Add an instruction label for the product list format
instruction_label = tk.Label(root, text="Example: 1312:Both:1, 1267:Single box:2")
instruction_label.grid(row=7, columnspan=2)

start_button = tk.Button(root, text="Start Bot", command=start_bot)
start_button.grid(row=8, column=0, sticky="ew")

stop_button = tk.Button(root, text="Stop Bot", command=stop_bot)
stop_button.grid(row=8, column=1, sticky="ew")

# Configure column and row weights to make the window resizable
root.columnconfigure(1, weight=1)
for i in range(9):
    root.rowconfigure(i, weight=1)

# Start the main loop
root.mainloop()

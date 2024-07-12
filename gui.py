import tkinter as tk
from tkinter import messagebox
import threading
import ctypes
import platform
from urllib.parse import urlparse
from datetime import datetime, timedelta
from main import check_product, prelaunch

stop_event = threading.Event()
stop_events = []
threads = []

# Define US time zones
us_timezones = ["Eastern", "Central", "Mountain", "Pacific"]

def set_app_icon():
    try:
        if platform.system() == 'Windows':
            app_icon = 'labubuicon.ico'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_icon)
            root.iconbitmap(app_icon)
        elif platform.system() == 'Darwin':  # macOS
            root.iconbitmap('@labubuicon.icns')
        else:  # Linux
            root.iconbitmap('@labubuicon.xbm')  # Use .xbm format for Linux
    except Exception as e:
        print(f"Error setting app icon: {e}")

def extract_product_number(url):
    try:
        parsed_url = urlparse(url)
        path_segments = parsed_url.path.split('/')
        if len(path_segments) > 3:
            return path_segments[3]
    except Exception as e:
        print(f"Error parsing URL: {e}")
    return None

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

    # Clear the stop event and threads list
    stop_event.clear()
    threads = []
    stop_events = []

    # Start threads for each product
    for row in product_rows:
        product_frame, url_entry, option_menu, quantity_entry, mode_var, tz_menu, day_menu, month_menu, year_menu, hour_menu, minute_menu = row
        product_url = url_entry.get().strip()
        product_number = extract_product_number(product_url)
        option = option_menu.cget("text")
        quantity = int(quantity_entry.get().strip())

        if mode_var.get() == "Restock":
            stop_event_local = threading.Event()
            stop_events.append(stop_event_local)
            thread = threading.Thread(target=check_product, args=(product_number, option, quantity, stop_event_local, user_email, user_password, card_number, card_expiry_date, card_security_code, card_holder_name))
        else:
            date_str = f"{year_menu.cget('text')}-{month_menu.cget('text')}-{day_menu.cget('text')}"
            launch_time = f"{date_str} {hour_menu.cget('text')}:{minute_menu.cget('text')}:00"
            tz = tz_menu.cget("text")
            stop_event_local = threading.Event()
            stop_events.append(stop_event_local)
            thread = threading.Thread(target=prelaunch, args=(product_number, option, quantity, stop_event_local, user_email, user_password, card_number, card_expiry_date, card_security_code, card_holder_name, launch_time, tz))

        threads.append(thread)
        thread.start()

    # messagebox.showinfo("Info", "Bot started.")

def stop_bot():
    global stop_events, threads

    for stop_event_local in stop_events:
        stop_event_local.set()

    for thread in threads:
        thread.join()

    stop_events.clear()
    threads.clear()

    messagebox.showinfo("Info", "Bot stopped")

def add_more_products():
    row = len(product_rows) + 1
    product_frame = tk.Frame(product_frame_container_inner)
    product_frame.grid(row=row, column=0, columnspan=10, padx=5, pady=5, sticky='ew')

    url_label = tk.Label(product_frame, text="Product URL")
    url_label.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
    url_entry = tk.Entry(product_frame, width=50)
    url_entry.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

    option_label = tk.Label(product_frame, text="Buying Option")
    option_label.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
    option_var = tk.StringVar(value="None")
    option_menu = tk.OptionMenu(product_frame, option_var, "None", "Single box", "Whole set", "Both")
    option_menu.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

    quantity_label = tk.Label(product_frame, text="Quantity")
    quantity_label.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
    quantity_entry = tk.Entry(product_frame, width=5)
    quantity_entry.grid(row=1, column=2, padx=5, pady=5, sticky='ew')
    quantity_entry.insert(0, "1")

    mode_label = tk.Label(product_frame, text="Mode")
    mode_label.grid(row=0, column=3, padx=5, pady=5, sticky='ew')
    mode_var = tk.StringVar(value="Restock")
    mode_menu = tk.OptionMenu(product_frame, mode_var, "Restock", "Prelaunch", command=lambda value, r=row: show_prelaunch_fields(r, value))
    mode_menu.grid(row=1, column=3, padx=5, pady=5, sticky='ew')

    tz_label = tk.Label(product_frame, text="Time Zone")
    tz_label.grid(row=0, column=4, padx=5, pady=5, sticky='ew')
    tz_var = tk.StringVar(value="Eastern")
    tz_menu = tk.OptionMenu(product_frame, tz_var, *us_timezones, command=lambda value, r=row: update_time_fields(r))
    tz_menu.grid(row=1, column=4, padx=5, pady=5, sticky='ew')

    day_label = tk.Label(product_frame, text="Day")
    day_label.grid(row=0, column=5, padx=5, pady=5, sticky='ew')
    day_var = tk.StringVar(value="01")
    day_menu = tk.OptionMenu(product_frame, day_var, *get_day_options())
    day_menu.grid(row=1, column=5, padx=5, pady=5, sticky='ew')

    month_label = tk.Label(product_frame, text="Month")
    month_label.grid(row=0, column=6, padx=5, pady=5, sticky='ew')
    month_var = tk.StringVar(value="01")
    month_menu = tk.OptionMenu(product_frame, month_var, *get_month_options())
    month_menu.grid(row=1, column=6, padx=5, pady=5, sticky='ew')

    year_label = tk.Label(product_frame, text="Year")
    year_label.grid(row=0, column=7, padx=5, pady=5, sticky='ew')
    year_var = tk.StringVar(value=str(datetime.now().year))
    year_menu = tk.OptionMenu(product_frame, year_var, *get_year_options())
    year_menu.grid(row=1, column=7, padx=5, pady=5, sticky='ew')

    hour_label = tk.Label(product_frame, text="Hour")
    hour_label.grid(row=0, column=8, padx=5, pady=5, sticky='ew')
    hour_var = tk.StringVar(value="00")
    hour_menu = tk.OptionMenu(product_frame, hour_var, *get_hour_options())
    hour_menu.grid(row=1, column=8, padx=5, pady=5, sticky='ew')

    minute_label = tk.Label(product_frame, text="Minute")
    minute_label.grid(row=0, column=9, padx=5, pady=5, sticky='ew')
    minute_var = tk.StringVar(value="00")
    minute_menu = tk.OptionMenu(product_frame, minute_var, *get_minute_options(hour_var.get()))
    minute_menu.grid(row=1, column=9, padx=5, pady=5, sticky='ew')

    tz_menu.grid_remove()
    day_menu.grid_remove()
    month_menu.grid_remove()
    year_menu.grid_remove()
    hour_menu.grid_remove()
    minute_menu.grid_remove()

    product_rows.append((product_frame, url_entry, option_menu, quantity_entry, mode_var, tz_menu, day_menu, month_menu, year_menu, hour_menu, minute_menu))

    product_frame_container_inner.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def remove_last_product():
    if len(product_rows) > 1:
        last_row = product_rows.pop()
        for widget in last_row:
            widget.grid_forget()
            widget.destroy()

        adjust_window_height()
    else:
        messagebox.showinfo("Info", "At least one product row must be present.")

def adjust_window_height():
    product_frame_container_inner.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def show_prelaunch_fields(row, mode):
    product_frame, _, _, _, _, tz_menu, day_menu, month_menu, year_menu, hour_menu, minute_menu = product_rows[row - 1]
    if mode == "Prelaunch":
        tz_menu.grid()
        day_menu.grid()
        month_menu.grid()
        year_menu.grid()
        hour_menu.grid()
        minute_menu.grid()
    else:
        tz_menu.grid_remove()
        day_menu.grid_remove()
        month_menu.grid_remove()
        year_menu.grid_remove()
        hour_menu.grid_remove()
        minute_menu.grid_remove()

def update_time_fields(row):
    product_frame, _, _, _, _, tz_menu, day_menu, month_menu, year_menu, hour_menu, minute_menu = product_rows[row - 1]
    hour_var = hour_menu.cget('textvariable')
    minute_var = minute_menu.cget('textvariable')

    hour_menu['menu'].delete(0, 'end')
    for hour in get_hour_options():
        hour_menu['menu'].add_command(label=hour, command=tk._setit(hour_var, hour))

    minute_menu['menu'].delete(0, 'end')
    for minute in get_minute_options(hour_var.get()):
        minute_menu['menu'].add_command(label=minute, command=tk._setit(minute_var, minute))

def extract_product_number(url):
    try:
        parts = url.split('/')
        return parts[parts.index('products') + 1]
    except Exception as e:
        messagebox.showerror("Error", f"Invalid product URL: {url}")
        return None

def get_day_options():
    today = datetime.now()
    days_in_month = (datetime(today.year, today.month + 1, 1) - timedelta(days=1)).day
    return ["{:02d}".format(i) for i in range(today.day, days_in_month + 1)]

def get_month_options():
    current_month = datetime.now().month
    return ["{:02d}".format(i) for i in range(current_month, 13)]

def get_year_options():
    current_year = datetime.now().year
    return [str(i) for i in range(current_year, current_year + 5)]

def get_hour_options():
    current_hour = datetime.now().hour
    return ["{:02d}".format(i) for i in range(current_hour, 24)]

def get_minute_options(selected_hour):
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute
    if int(selected_hour) == current_hour:
        return ["{:02d}".format(i) for i in range(current_minute + 1, 60)]
    else:
        return ["{:02d}".format(i) for i in range(60)]

root = tk.Tk()
root.title("Checkout Bot")
root.update_idletasks()
initial_width = root.winfo_width() + 875
initial_height = root.winfo_height() + 375
root.geometry(f"{initial_width}x{initial_height}")

root.resizable(False, False)
set_app_icon()

start_button = tk.Button(root, text="Start Bot", command=start_bot)
stop_button = tk.Button(root, text="Stop Bot", command=stop_bot)
start_button.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
stop_button.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

add_button = tk.Button(root, text="Add More Products", command=add_more_products)
remove_button = tk.Button(root, text="Remove Last Product", command=remove_last_product)
add_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
remove_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

canvas = tk.Canvas(root)
canvas.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.grid(row=3, column=2, sticky='ns')

canvas.configure(yscrollcommand=scrollbar.set)

product_frame_container = tk.Frame(canvas)
canvas.create_window((0, 0), window=product_frame_container, anchor='nw')

product_frame_container_inner = tk.Frame(product_frame_container)
product_frame_container_inner.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

product_rows = []
add_more_products()

user_details_frame = tk.Frame(root)
user_details_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

tk.Label(user_details_frame, text="Card Number:").grid(row=0, column=0, sticky="w")
card_number_entry = tk.Entry(user_details_frame)
card_number_entry.grid(row=0, column=1, sticky="ew")

tk.Label(user_details_frame, text="Expiry Date (MM/YY):").grid(row=1, column=0, sticky="w")
card_expiry_entry = tk.Entry(user_details_frame)
card_expiry_entry.grid(row=1, column=1, sticky="ew")

tk.Label(user_details_frame, text="Security Code:").grid(row=2, column=0, sticky="w")
security_code_entry = tk.Entry(user_details_frame)
security_code_entry.grid(row=2, column=1, sticky="ew")

tk.Label(user_details_frame, text="Card Holder Name:").grid(row=3, column=0, sticky="w")
card_holder_name_entry = tk.Entry(user_details_frame)
card_holder_name_entry.grid(row=3, column=1, sticky="ew")

tk.Label(user_details_frame, text="Email:").grid(row=4, column=0, sticky="w")
email_entry = tk.Entry(user_details_frame)
email_entry.grid(row=4, column=1, sticky="ew")

tk.Label(user_details_frame, text="Password:").grid(row=5, column=0, sticky="w")
password_entry = tk.Entry(user_details_frame, show="*")
password_entry.grid(row=5, column=1, sticky="ew")

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
product_frame_container_inner.columnconfigure(0, weight=1)
product_frame_container_inner.columnconfigure(1, weight=1)
product_frame_container_inner.columnconfigure(2, weight=1)
product_frame_container_inner.columnconfigure(3, weight=1)
product_frame_container_inner.columnconfigure(4, weight=1)
product_frame_container_inner.columnconfigure(5, weight=1)
product_frame_container_inner.columnconfigure(6, weight=1)
product_frame_container_inner.columnconfigure(7, weight=1)
product_frame_container_inner.columnconfigure(8, weight=1)
product_frame_container_inner.columnconfigure(9, weight=1)
user_details_frame.columnconfigure(0, weight=1)
user_details_frame.columnconfigure(1, weight=1)

product_frame_container_inner.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))

root.mainloop()

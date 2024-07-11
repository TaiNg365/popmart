# config.py
import threading

# Shared state
stop_event = threading.Event()
stop_events = []
threads = []
checkout_lock = threading.Lock()

# User Information
card_number = ""
card_expiry_date = ""
card_security_code = ""
card_holder_name = ""
user_email = ""
user_password = ""

# List of products and their purchase options (this will be filled by the GUI)
product_list = {}


# Popmart Checkout Bot

This project is a checkout bot for Popmart products. It allows users to automatically add products to their cart and proceed to checkout using a graphical user interface (GUI).

## Features

- Supports both restock and prelaunch modes.
- Allows users to specify multiple products and their purchase options.
- Automatically fills in user details for checkout.
- Supports various US time zones for prelaunch scheduling.

## Requirements

- Python 3.9+
- Google Chrome browser
- Chromedriver (compatible with your version of Chrome)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/TaiNg365/popmart.git
   cd popmart

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **Install the dependencies:**
   
   ```bash
   pip install -r requirements.txt

4. **Download Chromedriver:**

   Download the appropriate version of Chromedriver from the official site and place it in the root directory of the project.

## Usage

### Running the GUI

1. **Run the GUI application:**

   ```bash
   python gui.py

2. **Using the GUI:**

   - Product URL: Enter the URL of the product page on the Popmart website.
   - Buying Option: Select the desired buying option (Single box, Whole set, Both or None).
   - Quantity: Enter the quantity you want to purchase.
   - Mode: Choose between "Restock" and "Prelaunch".
   - Prelaunch Settings (only visible in Prelaunch mode):
      - Time Zone: Select your time zone.
      - Day, Month, Year, Hour, Minute: Set the launch time for the product.
   - User Details: Enter your card details, email, and password

3.  **Control Buttons:**

   - Start Bot: Starts the bot to monitor and purchase the products.
   - Stop Bot: Stops the bot.
   - Add More Products: Adds additional rows for more products.
   - Remove Last Product: Removes the last product row.

## Building Executable

You can use GitHub Actions to build executables for Windows, macOS, and Linux.

1. **Ensure the chromedriver is included in the pyinstaller specification file.**
2. **Run GitHub Actions:**

   Make sure your .github/workflows/build.yml file is set up correctly to build executables for all platforms.

3. **After a successful build, download the artifacts from GitHub Actions.**

## Manually Building Executables

To manually build the executables, follow these steps:

1. **Ensure you have pyinstaller installed:**

   ```bash
   pip install pyinstaller

2. **Build the executables:**

   ```bash
   pyinstaller gui.spec

3. **Make the executable runnable (macOS/Linux):**

   ```bash
   chmod +x dist/gui/gui


## Troubleshooting

- Chromedriver issues: Ensure that the chromedriver version matches your installed Chrome version.
- GUI issues on macOS: If the GUI does not respond properly, ensure you have the correct permissions and that tkinter is properly installed.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

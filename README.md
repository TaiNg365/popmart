
# Popmart Auto Checkout Bot

## Purpose

The Popmart Auto Checkout Bot is designed to automate the process of purchasing products from the Popmart website. The primary goal is to help users secure products during new launches or restocks, which can occur at random times. This bot ensures that the desired products are added to the cart and purchased as soon as they become available, saving users the hassle of constantly monitoring the website.

## Features

- Automatically logs into the Popmart website with provided user credentials.
- Continuously monitors specified products for availability.
- Automatically selects purchase options (Whole Set, Single Box, etc.) and quantity.
- Adds products to the cart and proceeds to checkout.
- Handles multiple products simultaneously using multithreading.
- Displays a success message in the GUI when a product is successfully purchased.

## User Guide

### Prerequisites

- Python 3.9 or higher
- Selenium WebDriver
- Google Chrome and ChromeDriver

### Installation

1. **Clone the Repository:**

   ```sh
   git clone https://github.com/yourusername/popmart-auto-checkout.git
   cd popmart-auto-checkout
   ```

2. **Install the Required Packages:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Download ChromeDriver:**

   Download the ChromeDriver from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads) and place it in the project directory.

### Usage

1. **Run the Application:**

   ```sh
   python gui.py
   ```

2. **Fill in the User Information:**

   - Card Number
   - Expiry Date (MM/YY)
   - Security Code
   - Card Holder Name
   - Email
   - Password

3. **Specify the Product List:**

   Enter the products in the format: `product_id:option:quantity`. For example:
   ```
   1312:Both:1, 1267:Single box:2, 908:None:3
   ```

   - `product_id` is the ID of the product on the Popmart website.
   - `option` can be `Whole Set`, `Single Box`, or `None` for products without specific purchase options.
   - `quantity` is the number of items to purchase.

4. **Start the Bot:**

   Click the `Start Bot` button. The bot will begin monitoring the specified products and attempt to purchase them as soon as they become available.

5. **Stop the Bot:**

   Click the `Stop Bot` button to stop all running threads and clear the input fields.

### Building an Executable

To share the application with others without requiring them to install Python and dependencies:

1. **Install PyInstaller:**

   ```sh
   pip install pyinstaller
   ```

2. **Create an Executable:**

   ```sh
   pyinstaller --onefile --windowed --icon=labuicon.ico gui.py
   ```

   The executable will be created in the `dist` directory.

### Cross-Platform Considerations

Currently, this project is designed to run on Windows. To run on macOS or Linux, you will need to adjust the ChromeDriver path accordingly in `main.py`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Feel free to contribute to this project by submitting issues or pull requests. For major changes, please open an issue first to discuss what you would like to change.

Enjoy automated shopping with the Popmart Auto Checkout Bot!
```

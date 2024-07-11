import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import threading
import time

# Determine the path to chromedriver based on whether the script is frozen or not
if getattr(sys, 'frozen', False):
    chromedriver_path = os.path.join(sys._MEIPASS, 'chromedriver.exe' if sys.platform == 'win32' else 'chromedriver')
else:
    chromedriver_path = 'chromedriver.exe' if sys.platform == 'win32' else './chromedriver'  # Adjust for macOS and Linux

# Function to handle each product
def check_product(product, purchase_option, quantity, stop_event_local, user_email, user_password, card_number, card_expiry_date, card_security_code, card_holder_name):
    print(f"Checking product {product} with purchase option {purchase_option} and quantity {quantity}")

    # Create a new WebDriver instance for each product
    service = Service(chromedriver_path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(f'https://www.popmart.com/us/products/{product}')

    def accept_policy():
        try:
            accept_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "policy_acceptBtn__ZNU71") and text()="ACCEPT"]'))
            )
            accept_button.click()
            print(f"Accepted policy for product {product}")
        except Exception as e:
            print(f"No policy prompt for product {product}: {e}")

    def sign_in():
        signed_in = False
        retry_count = 0
        while not signed_in and retry_count < 3:
            try:
                sign_in_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "header_infoTitle__Fse4B ") and text()="Sign in / Register"]'))
                )
                sign_in_button.click()
                print(f"Clicked Sign in for product {product}")

                email_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@id="email" and @placeholder="Enter your e-mail address"]'))
                )
                email_input.send_keys(user_email)
                print(f"Entered email for product {product}")

                continue_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//button[@type="button" and contains(@class, "ant-btn-primary") and text()="CONTINUE"]'))
                )
                continue_button.click()
                print(f"Clicked Continue for product {product}")

                password_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@id="password" and @placeholder="Enter your password"]'))
                )
                password_input.send_keys(user_password)
                print(f"Entered password for product {product}")

                sign_in_submit_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//button[@type="submit" and contains(@class, "ant-btn-primary") and text()="SIGN IN"]'))
                )
                sign_in_submit_button.click()
                print(f"Clicked Sign in submit for product {product}")
                time.sleep(5)  # Wait for 5 seconds to ensure sign-in completes
                signed_in = True
            except Exception as e:
                print(f"Sign in process failed for product {product}, retrying... ({retry_count+1}/3): {e}")
                retry_count += 1
                driver.get(f'https://www.popmart.com/us/products/{product}')
                accept_policy()

        if not signed_in:
            print(f"Failed to sign in for product {product} after 3 attempts.")
            driver.quit()
            return False
        return True

    accept_policy()
    if not sign_in():
        return

    driver.get(f'https://www.popmart.com/us/products/{product}')
    add_to_cart_success = False

    while not add_to_cart_success and not stop_event_local.is_set():
        options_to_try = [purchase_option] if purchase_option and purchase_option.lower() in ['whole set', 'single box'] else [None]

        option_found = False
        for option in options_to_try:
            try:
                if option:
                    option_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, f'//div[contains(@class, "index_sizeInfoTitle__kpZbS") and contains(text(), "{option}")]'))
                    )
                    option_element.click()
                    option_found = True
                    time.sleep(1)  # Short delay to allow the page to update

                # If Single Box is selected, change the quantity to the specified quantity
                if not option or option.lower() == 'single box':
                    try:
                        quantity_input = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//input[@type="number" and contains(@class, "index_countInput__2ma_C")]'))
                        )
                        quantity_input.click()
                        quantity_input.send_keys(Keys.CONTROL + "a")
                        quantity_input.send_keys(Keys.DELETE)
                        quantity_input.send_keys(str(quantity))
                        time.sleep(1)  # Wait for 2 seconds to ensure the quantity is updated
                    except Exception as e:
                        print(f"Quantity input field not found or not clickable for product {product}")

                # Try to click "Add to Cart"
                try:
                    add_to_cart_button = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "index_usBtn__2KlEx") and contains(@class, "index_btnFull__F7k90") and (contains(@class, "index_red__kx6Ql") or contains(@class, "index_black__RgEgP")) and text()="ADD TO BAG"]'))
                    )
                    add_to_cart_button.click()
                    print(f"Add to cart button clicked for product {product} with option {option}")
                    add_to_cart_success = True
                    stop_event_local.set()  # Signal this thread to stop
                    break  # Exit the loop once the button is clicked
                except Exception as e:
                    print(f"Add to cart button not found or not clickable for product {product} with option {option}")

            except Exception as e:
                print(f"Option {option} not found or not clickable for product {product}")

        # If no option found, directly handle quantity and add to cart
        if not option_found:
            try:
                quantity_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@type="number" and contains(@class, "index_countInput__2ma_C")]'))
                )
                quantity_input.click()
                quantity_input.send_keys(Keys.CONTROL + "a")
                quantity_input.send_keys(Keys.DELETE)
                quantity_input.send_keys(str(quantity))
                time.sleep(2)  # Wait for 2 seconds to ensure the quantity is updated

                add_to_cart_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "index_usBtn__2KlEx") and contains(@class, "index_btnFull__F7k90") and (contains(@class, "index_red__kx6Ql") or contains(@class, "index_black__RgEgP")) and text()="ADD TO BAG"]'))
                )
                add_to_cart_button.click()
                print(f"Add to cart button clicked for product {product} without specific option")
                add_to_cart_success = True
                stop_event_local.set()  # Signal this thread to stop
            except Exception as e:
                print(f"Add to cart button not found or not clickable for product {product} without specific option")

        # Refresh the page if "Add to Cart" button is not found
        if not add_to_cart_success:
            time.sleep(1)  # Wait for 2 seconds before refreshing
            driver.refresh()

    # Proceed with checkout process only if "Add to Cart" was successful
    if add_to_cart_success:
        print(f"Proceeding to checkout for product {product}")

        # Wait for the "Go to Bag" icon to be present and click it
        try:
            go_to_bag_icon = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="index_infoIcon__5cYJX index_container__wMsmd "]'))
            )
            go_to_bag_icon.click()
        except Exception as e:
            print(f"Go to Bag icon not found or not clickable for product {product}")

        # Proceed only if the cart is not empty
        try:
            # Wait for the "select all" checkbox and click it
            select_all_checkbox = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'index_checkbox__w_166'))
            )
            select_all_checkbox.click()

            # Wait for the "CHECK OUT" button to be present and click it
            checkout_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//button[@type="button" and contains(@class, "ant-btn") and contains(@class, "ant-btn-primary") and contains(@class, "ant-btn-dangerous") and contains(@class, "index_checkout__V9YPC") and text()="CHECK OUT"]'))
            )
            checkout_button.click()
            time.sleep(1)  # Wait for 1 second

            # Wait for the "CreditCard" option to be present and click it
            credit_card_option = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "directPay_left__jh8vj") and not(contains(@class, "directPay_leftActivity__raNnL"))]'))
            )
            credit_card_option.click()
            time.sleep(5)  # Wait for 5 seconds

            # Enter the card number
            card_number_iframe = None
            while not card_number_iframe:
                try:
                    card_number_iframe = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//iframe[@title="Iframe for card number"]'))
                    )
                except Exception as e:
                    print("Waiting for card number iframe...")
                    time.sleep(1)

            driver.switch_to.frame(card_number_iframe)
            try:
                card_number_field = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'js-iframe-input'))
                )
                card_number_field.send_keys(card_number)  # Replace with your actual card number
                time.sleep(1)  # Wait for 1 second
            except Exception as e:
                print(f"Card number input field not found or not clickable: {e}")
            finally:
                driver.switch_to.default_content()

            # Enter the expiration date
            expiration_date_iframe = None
            while not expiration_date_iframe:
                try:
                    expiration_date_iframe = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//iframe[@title="Iframe for expiry date"]'))
                    )
                except Exception as e:
                    print("Waiting for expiration date iframe...")
                    time.sleep(1)

            driver.switch_to.frame(expiration_date_iframe)
            try:
                expiration_date_field = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'js-iframe-input'))
                )
                expiration_date_field.send_keys(card_expiry_date)  # Replace with your actual expiration date
                time.sleep(1)  # Wait for 1 second
            except Exception as e:
                print(f"Expiration date input field not found or not clickable: {e}")
            finally:
                driver.switch_to.default_content()

            # Enter the security code
            security_code_iframe = None
            while not security_code_iframe:
                try:
                    security_code_iframe = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//iframe[@title="Iframe for security code"]'))
                    )
                except Exception as e:
                    print("Waiting for security code iframe...")
                    time.sleep(1)

            driver.switch_to.frame(security_code_iframe)
            try:
                security_code_field = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'js-iframe-input'))
                )
                security_code_field.send_keys(card_security_code)  # Replace with your actual security code
                time.sleep(1)  # Wait for 1 second
            except Exception as e:
                print(f"Security code input field not found or not clickable: {e}")
            finally:
                driver.switch_to.default_content()

            # Enter the name on the card
            try:
                card_name_field = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@placeholder="J. Smith" and @name="holderName"]'))
                )
                card_name_field.send_keys(card_holder_name)  # Replace with your actual card name
                time.sleep(1)  # Wait for 1 second
            except Exception as e:
                print(f"Card name input field not found or not clickable: {e}")

            # Click the "Pay" button
            try:
                pay_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//button[@class="adyen-checkout__button adyen-checkout__button--pay"]'))
                )
                pay_button.click()
                time.sleep(5)  # Wait for 1 second
                print(f"Successfully purchased product {product}")
                driver.quit()  # Close the driver for this product only if purchase is successful
            except Exception as e:
                print(f"Pay button not found or not clickable: {e}")

        except Exception as e:
            print("Cart is empty or an error occurred before proceeding to checkout: ", e)

    else:
        driver.quit()  # Close the driver if "Add to Cart" was not successful

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
from datetime import datetime, timedelta
import pytz

# Determine the path to chromedriver based on whether the script is frozen or not
if getattr(sys, 'frozen', False):
    chromedriver_path = os.path.join(sys._MEIPASS, 'chromedriver.exe' if sys.platform == 'win32' else 'chromedriver')
else:
    chromedriver_path = 'chromedriver.exe' if sys.platform == 'win32' else './chromedriver'  # Adjust for macOS and Linux

def wait_for_element(driver, by, value, retries=3, timeout=1):
    for i in range(retries):
        try:
            return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        except Exception as e:
            if i < retries - 1:
                time.sleep(0.5)  # brief pause before retrying
                continue
            else:
                raise e
            
def check_product(product, purchase_option, quantity, stop_event_local, user_email, user_password, card_number, card_expiry_date, card_security_code, card_holder_name):
    print(f"Checking product {product} with purchase option {purchase_option} and quantity {quantity}")

    # Create a new WebDriver instance for each product
    service = Service(chromedriver_path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(f'https://www.popmart.com/us/products/{product}')

    def accept_policy():
        try:
            accept_button = wait_for_element(driver, By.XPATH, '//div[contains(@class, "policy_acceptBtn__ZNU71") and text()="ACCEPT"]')
            accept_button.click()
            print(f"Accepted policy for product {product}")
        except Exception as e:
            print(f"No policy prompt for product {product}: {e}")

    def sign_in():
        signed_in = False
        retry_count = 0
        while not signed_in and retry_count < 3:
            try:
                sign_in_button = wait_for_element(driver, By.XPATH, '//div[contains(@class, "header_infoTitle__Fse4B ") and text()="Sign in / Register"]')
                sign_in_button.click()
                print(f"Clicked Sign in for product {product}")

                email_input = wait_for_element(driver, By.XPATH, '//input[@id="email" and @placeholder="Enter your e-mail address"]')
                email_input.send_keys(user_email)
                print(f"Entered email for product {product}")

                continue_button = wait_for_element(driver, By.XPATH, '//button[@type="button" and contains(@class, "ant-btn-primary") and text()="CONTINUE"]')
                continue_button.click()
                print(f"Clicked Continue for product {product}")

                password_input = wait_for_element(driver, By.XPATH, '//input[@id="password" and @placeholder="Enter your password"]')
                password_input.send_keys(user_password)
                print(f"Entered password for product {product}")

                sign_in_submit_button = wait_for_element(driver, By.XPATH, '//button[@type="submit" and contains(@class, "ant-btn-primary") and text()="SIGN IN"]')
                sign_in_submit_button.click()
                print(f"Clicked Sign in submit for product {product}")
                time.sleep(2)  # Wait for 2 seconds to ensure sign-in completes
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
                    option_element = wait_for_element(driver, By.XPATH, f'//div[contains(@class, "index_sizeInfoTitle__kpZbS") and contains(text(), "{option}")]')
                    option_element.click()
                    option_found = True

                    if option.lower() == 'single box':
                        quantity_input = wait_for_element(driver, By.XPATH, '//input[@type="number" and contains(@class, "index_countInput__2ma_C")]')
                        quantity_input.click()
                        quantity_input.send_keys(Keys.CONTROL + "a")
                        quantity_input.send_keys(Keys.DELETE)
                        quantity_input.send_keys(str(quantity))

                add_to_cart_button = wait_for_element(driver, By.XPATH, '//div[contains(@class, "index_usBtn__2KlEx") and contains(@class, "index_btnFull__F7k90") and (contains(@class, "index_red__kx6Ql") or contains(@class, "index_black__RgEgP")) and text()="ADD TO BAG"]')
                add_to_cart_button.click()
                print(f"Add to cart button clicked for product {product} with option {option}")
                add_to_cart_success = True
                stop_event_local.set()  # Signal this thread to stop
                break  # Exit the loop once the button is clicked

            except Exception as e:
                print(f"Option {option} not found or not clickable for product {product}: {e}")

        if not option_found:
            try:
                quantity_input = wait_for_element(driver, By.XPATH, '//input[@type="number" and contains(@class, "index_countInput__2ma_C")]')
                quantity_input.click()
                quantity_input.send_keys(Keys.CONTROL + "a")
                quantity_input.send_keys(Keys.DELETE)
                quantity_input.send_keys(str(quantity))

                add_to_cart_button = wait_for_element(driver, By.XPATH, '//div[contains(@class, "index_usBtn__2KlEx") and contains(@class, "index_btnFull__F7k90") and (contains(@class, "index_red__kx6Ql") or contains(@class, "index_black__RgEgP")) and text()="ADD TO BAG"]')
                add_to_cart_button.click()
                print(f"Add to cart button clicked for product {product} without specific option")
                add_to_cart_success = True
                stop_event_local.set()  # Signal this thread to stop
            except Exception as e:
                print(f"Add to cart button not found or not clickable for product {product} without specific option: {e}")

        if not add_to_cart_success:
            driver.refresh()
            time.sleep(0.5)  # Brief pause before retrying

    if add_to_cart_success:
        print(f"Proceeding to checkout for product {product}")

        try:
            go_to_bag_icon = wait_for_element(driver, By.XPATH, '//div[@class="index_infoIcon__5cYJX index_container__wMsmd "]')
            go_to_bag_icon.click()
        except Exception as e:
            print(f"Go to Bag icon not found or not clickable for product {product}")

        try:
            select_all_checkbox = wait_for_element(driver, By.CLASS_NAME, 'index_checkbox__w_166')
            select_all_checkbox.click()

            checkout_button = wait_for_element(driver, By.XPATH, '//button[@type="button" and contains(@class, "ant-btn") and contains(@class, "ant-btn-primary") and contains(@class, "ant-btn-dangerous") and contains(@class, "index_checkout__V9YPC") and text()="CHECK OUT"]')
            checkout_button.click()
            time.sleep(2)

            credit_card_option = wait_for_element(driver, By.XPATH, '//div[contains(@class, "directPay_left__jh8vj") and not(contains(@class, "directPay_leftActivity__raNnL"))]')
            credit_card_option.click()
            time.sleep(1)

            def enter_iframe_input(iframe_xpath, input_xpath, value):
                driver.switch_to.frame(wait_for_element(driver, By.XPATH, iframe_xpath))
                input_field = wait_for_element(driver, By.CLASS_NAME, input_xpath)
                input_field.send_keys(value)
                driver.switch_to.default_content()

            enter_iframe_input('//iframe[@title="Iframe for card number"]', 'js-iframe-input', card_number)
            enter_iframe_input('//iframe[@title="Iframe for expiry date"]', 'js-iframe-input', card_expiry_date)
            enter_iframe_input('//iframe[@title="Iframe for security code"]', 'js-iframe-input', card_security_code)

            card_name_field = wait_for_element(driver, By.XPATH, '//input[@placeholder="J. Smith" and @name="holderName"]')
            card_name_field.send_keys(card_holder_name)

            pay_button = wait_for_element(driver, By.XPATH, '//button[@class="adyen-checkout__button adyen-checkout__button--pay"]')
            pay_button.click()
            time.sleep(2)
            print(f"Successfully purchased product {product}")
        except Exception as e:
            print(f"Checkout process failed for product {product}: {e}")
        finally:
            driver.quit()


def prelaunch(product, purchase_option, quantity, stop_event_local, user_email, user_password, card_number, card_expiry_date, card_security_code, card_holder_name, launch_time, time_zone):
    print(f"Checking prelaunch product {product} with purchase option {purchase_option}, quantity {quantity}, and launch time {launch_time}")

    # Create a new WebDriver instance for each product
    service = Service(chromedriver_path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(f'https://www.popmart.com/us/products/{product}')

    def wait_for_element(driver, by, value, retries=3, timeout=1):
        for i in range(retries):
            try:
                return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
            except Exception as e:
                if i < retries - 1:
                    time.sleep(0.5)  # brief pause before retrying
                    continue
                else:
                    raise e

    def accept_policy():
        try:
            accept_button = wait_for_element(driver, By.XPATH, '//div[contains(@class, "policy_acceptBtn__ZNU71") and text()="ACCEPT"]')
            accept_button.click()
            print(f"Accepted policy for product {product}")
        except Exception as e:
            print(f"No policy prompt for product {product}: {e}")

    def sign_in():
        signed_in = False
        retry_count = 0
        while not signed_in and retry_count < 3:
            try:
                sign_in_button = wait_for_element(driver, By.XPATH, '//div[contains(@class, "header_infoTitle__Fse4B ") and text()="Sign in / Register"]')
                sign_in_button.click()
                print(f"Clicked Sign in for product {product}")

                email_input = wait_for_element(driver, By.XPATH, '//input[@id="email" and @placeholder="Enter your e-mail address"]')
                email_input.send_keys(user_email)
                print(f"Entered email for product {product}")

                continue_button = wait_for_element(driver, By.XPATH, '//button[@type="button" and contains(@class, "ant-btn-primary") and text()="CONTINUE"]')
                continue_button.click()
                print(f"Clicked Continue for product {product}")

                password_input = wait_for_element(driver, By.XPATH, '//input[@id="password" and @placeholder="Enter your password"]')
                password_input.send_keys(user_password)
                print(f"Entered password for product {product}")

                sign_in_submit_button = wait_for_element(driver, By.XPATH, '//button[@type="submit" and contains(@class, "ant-btn-primary") and text()="SIGN IN"]')
                sign_in_submit_button.click()
                print(f"Clicked Sign in submit for product {product}")
                time.sleep(2)  # Wait for 2 seconds to ensure sign-in completes
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
    
    # Add to cart logic
    try:
        option_element = wait_for_element(driver, By.XPATH, f'//div[contains(@class, "index_sizeInfoTitle__kpZbS") and contains(text(), "{purchase_option}")]')
        option_element.click()
        time.sleep(0.5)  # Short delay to allow the page to update

        if purchase_option.lower() == 'single box':
            quantity_input = wait_for_element(driver, By.XPATH, '//input[@type="number" and contains(@class, "index_countInput__2ma_C")]')
            quantity_input.click()
            quantity_input.send_keys(Keys.CONTROL + "a")
            quantity_input.send_keys(Keys.DELETE)
            quantity_input.send_keys(str(quantity))
            time.sleep(0.5)  # Short delay to ensure the quantity is updated

        add_to_cart_button = wait_for_element(driver, By.XPATH, '//div[contains(@class, "index_usBtn__2KlEx") and contains(@class, "index_btnFull__F7k90") and (contains(@class, "index_red__kx6Ql") or contains(@class, "index_black__RgEgP")) and text()="ADD TO BAG"]')
        add_to_cart_button.click()
        print(f"Add to cart button clicked for product {product} with option {purchase_option}")

    except Exception as e:
        print(f"Add to cart failed for product {product} with option {purchase_option}: {e}")
        return

    # Proceed with checkout process only if "Add to Cart" was successful
    print(f"Proceeding to checkout for product {product}")

    # Wait for the "Go to Bag" icon to be present and click it
    try:
        go_to_bag_icon = wait_for_element(driver, By.XPATH, '//div[@class="index_infoIcon__5cYJX index_container__wMsmd "]')
        go_to_bag_icon.click()
        time.sleep(1)
    except Exception as e:
        print(f"Go to Bag icon not found or not clickable for product {product}")


    # Convert the launch time to the specified time zone
    tz = pytz.timezone(f'US/{time_zone}')
    launch_time_tz = tz.localize(datetime.strptime(launch_time, "%Y-%m-%d %H:%M:%S"))
    current_time = datetime.now(pytz.utc)

    while current_time < launch_time_tz:
        time_diff = (launch_time_tz - current_time).total_seconds()
        if time_diff > 0:
            print(f"Waiting for launch time: {launch_time_tz} (current time: {current_time}), sleeping for {min(time_diff, 60)} seconds.")
            time.sleep(1)  # Sleep briefly before checking again
            driver.refresh()
        current_time = datetime.now(pytz.utc)

    # Refresh the page at launch time
    print("Launch time reached, refreshing the page.")
    driver.refresh()

    # Proceed with checkout process
    try:
        checkout_successful = False
        while not checkout_successful:
            try:
                # Wait for the "select all" checkbox and click it
                select_all_checkbox = wait_for_element(driver, By.CLASS_NAME, 'index_checkbox__w_166')
                select_all_checkbox.click()

                # Wait for the "CHECK OUT" button to be present and click it
                checkout_button = wait_for_element(driver, By.XPATH, '//button[@type="button" and contains(@class, "ant-btn") and contains(@class, "ant-btn-primary") and contains(@class, "ant-btn-dangerous") and contains(@class, "index_checkout__V9YPC") and text()="CHECK OUT"]')
                checkout_button.click()
                time.sleep(2)  # Short delay

                # Wait for the "CreditCard" option to be present and click it
                credit_card_option = wait_for_element(driver, By.XPATH, '//div[contains(@class, "directPay_left__jh8vj") and not(contains(@class, "directPay_leftActivity__raNnL"))]')
                credit_card_option.click()
                time.sleep(1)  # Short delay

                def enter_iframe_input(iframe_xpath, input_xpath, value):
                    driver.switch_to.frame(wait_for_element(driver, By.XPATH, iframe_xpath))
                    input_field = wait_for_element(driver, By.CLASS_NAME, input_xpath)
                    input_field.send_keys(value)
                    driver.switch_to.default_content()

                enter_iframe_input('//iframe[@title="Iframe for card number"]', 'js-iframe-input', card_number)
                enter_iframe_input('//iframe[@title="Iframe for expiry date"]', 'js-iframe-input', card_expiry_date)
                enter_iframe_input('//iframe[@title="Iframe for security code"]', 'js-iframe-input', card_security_code)

                card_name_field = wait_for_element(driver, By.XPATH, '//input[@placeholder="J. Smith" and @name="holderName"]')
                card_name_field.send_keys(card_holder_name)

                pay_button = wait_for_element(driver, By.XPATH, '//button[@class="adyen-checkout__button adyen-checkout__button--pay"]')
                pay_button.click()
                time.sleep(2)  # Short delay
                checkout_successful = True
                print(f"Successfully purchased product {product}")
            except Exception as e:
                print(f"Checkout process failed for product {product}: {e}")
                driver.refresh()

    except Exception as e:
        print(f"Cart is empty or an error occurred before proceeding to checkout: {e}")

    # Only quit the driver after the purchase is successful
    driver.quit()


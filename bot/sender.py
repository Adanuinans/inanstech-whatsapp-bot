# sender.py
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

def send_message(driver, message_text):
    """
    Sends a message in the currently active chat
    """
    try:
        input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
        input_box.click()
        input_box.send_keys(message_text)
        time.sleep(0.5)
        input_box.send_keys("\n")  # Press Enter to send
        time.sleep(0.5)
    except NoSuchElementException:
        print("Unable to find message input box.")
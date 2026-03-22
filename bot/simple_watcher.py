# bot/simple_watcher.py
import time
import re
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def watch_messages(driver, router, state):
    print("=" * 50)
    print("WHATSAPP MESSAGE WATCHER STARTED")
    print("=" * 50)
    print("Waiting for WhatsApp to load...")
    time.sleep(10)
    print("WhatsApp loaded. Monitoring for messages...")
    
    processed_messages = set()
    
    while True:
        try:
            # Find all unread indicators
            unread_indicators = driver.find_elements(By.CSS_SELECTOR, "span[aria-label*='unread']")
            
            if unread_indicators:
                print(f"\n📬 Found {len(unread_indicators)} chat(s) with unread messages")
                
                for indicator in unread_indicators:
                    try:
                        # Find the chat row
                        chat_row = indicator.find_element(By.XPATH, "./ancestor::div[@role='row']")
                        
                        # Get chat name
                        name_el = chat_row.find_element(By.CSS_SELECTOR, "span[title]")
                        chat_name = name_el.get_attribute("title")
                        
                        print(f"Processing message from {chat_name}")
                        
                        # Click to open chat
                        chat_row.click()
                        time.sleep(2)
                        
                        # Get messages
                        messages = driver.find_elements(By.CSS_SELECTOR, "div[class*='message-in']")
                        
                        if messages:
                            latest_message = messages[-1].text.strip()
                            if latest_message:
                                print(f"Message: {latest_message}")
                                reply = router.route(chat_name, latest_message)
                                if reply:
                                    # Send reply
                                    input_box = driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
                                    input_box.click()
                                    input_box.send_keys(reply)
                                    time.sleep(0.5)
                                    input_box.send_keys(Keys.ENTER)
                                    print(f"Reply sent: {reply[:100]}...")
                                    
                    except Exception as e:
                        print(f"Error processing: {e}")
                        continue
            
            time.sleep(3)
            
        except Exception as e:
            print(f"Watcher error: {e}")
            time.sleep(5)

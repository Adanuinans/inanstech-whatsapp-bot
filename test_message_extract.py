from bot.driver import launch_browser
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_message_text(msg_element):
    text_selectors = [
        "span.selectable-text",
        "div.copyable-text",
        "span[data-testid='conversation-message-text']",
        "span[dir='auto']",
        "div[dir='auto']"
    ]
    
    for selector in text_selectors:
        try:
            text_elem = msg_element.find_element(By.CSS_SELECTOR, selector)
            text = text_elem.text
            if text:
                return text
        except:
            continue
    
    try:
        text = msg_element.text
        if text:
            return text
    except:
        pass
    
    return None

driver = launch_browser()
print("Scan QR code and wait...")
time.sleep(30)

# Find and click on a chat with unread messages
unread = driver.find_elements(By.CSS_SELECTOR, "span[aria-label*='unread']")
if unread:
    print(f"Found {len(unread)} unread chats")
    
    # Click on the first unread chat's parent
    try:
        unread[0].find_element(By.XPATH, "..").click()
        print("Clicked on chat")
        time.sleep(3)
        
        # Now look for the conversation panel
        print("\n" + "="*60)
        print("LOOKING FOR MESSAGES IN CONVERSATION")
        print("="*60)
        
        # Find the conversation panel
        conversation_selectors = [
            "div[data-testid='conversation-panel-messages']",
            "div[aria-label*='messages']",
            "div[role='application'] div[role='region']"
        ]
        
        conversation_panel = None
        for selector in conversation_selectors:
            try:
                conversation_panel = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"Found conversation panel with selector: {selector}")
                break
            except:
                continue
        
        if conversation_panel:
            # Now find all message rows inside the conversation panel
            message_rows = conversation_panel.find_elements(By.CSS_SELECTOR, "div[role='row']")
            print(f"\nFound {len(message_rows)} message rows in conversation")
            
            # Look at the last few messages
            for i, row in enumerate(message_rows[-5:]):  # Last 5 messages
                print(f"\nMessage {i+1}:")
                class_name = row.get_attribute("class")
                print(f"  Class: {class_name[:100] if class_name else 'None'}")
                
                # Check if it's an incoming message
                if "message-in" in (class_name or ""):
                    print("  Type: Incoming")
                elif "message-out" in (class_name or ""):
                    print("  Type: Outgoing (sent by us)")
                
                # Try to get text
                text = get_message_text(row)
                if text:
                    print(f"  Text: {text}")
                else:
                    print("  No text found")
            
            # Also try to find messages directly by class
            print("\n" + "="*60)
            print("FINDING MESSAGES BY CLASS")
            print("="*60)
            
            message_classes = [
                "message-in",
                "message-out",
                "copyable-text"
            ]
            
            for msg_class in message_classes:
                elements = conversation_panel.find_elements(By.CSS_SELECTOR, f"div[class*='{msg_class}']")
                print(f"Elements with class containing '{msg_class}': {len(elements)}")
                if elements:
                    for elem in elements[:3]:
                        text = get_message_text(elem)
                        if text:
                            print(f"  Text: {text}")
        else:
            print("Could not find conversation panel")
            
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No unread chats found")

input("\nPress Enter to close...")
driver.quit()
from bot.driver import launch_browser
import time
from selenium.webdriver.common.by import By

driver = launch_browser()
print("Browser launched. Please scan QR code and wait 30 seconds...")
time.sleep(30)

print("\n" + "="*60)
print("FINDING UNREAD MESSAGES STRUCTURE")
print("="*60)

# Find all unread indicators
unread_indicators = driver.find_elements(By.XPATH, "//span[contains(@aria-label, 'unread')]")
print(f"Found {len(unread_indicators)} unread indicators")

for i, indicator in enumerate(unread_indicators[:3]):
    print(f"\n--- Unread Indicator {i+1} ---")
    print(f"HTML: {indicator.get_attribute('outerHTML')}")
    
    # Try different ways to find parent
    print("\nTrying to find parent chat:")
    
    # Method 1: Go up by parent
    try:
        parent = indicator.find_element(By.XPATH, "..")
        print(f"  Parent 1: {parent.get_attribute('class')} - role: {parent.get_attribute('role')}")
    except Exception as e:
        print(f"  Parent 1 error: {e}")
    
    # Method 2: Go up 2 levels
    try:
        parent2 = indicator.find_element(By.XPATH, "../..")
        print(f"  Parent 2: {parent2.get_attribute('class')} - role: {parent2.get_attribute('role')}")
    except Exception as e:
        print(f"  Parent 2 error: {e}")
    
    # Method 3: Go up 3 levels
    try:
        parent3 = indicator.find_element(By.XPATH, "../../..")
        print(f"  Parent 3: {parent3.get_attribute('class')} - role: {parent3.get_attribute('role')}")
    except Exception as e:
        print(f"  Parent 3 error: {e}")
    
    # Method 4: Find by XPath ancestor
    try:
        ancestor = indicator.find_element(By.XPATH, "./ancestor::div[contains(@class, '_ak8q')]")
        print(f"  Found by class _ak8q: {ancestor.get_attribute('class')}")
    except Exception as e:
        print(f"  Ancestor _ak8q error: {e}")
    
    # Method 5: Find by XPath ancestor with role
    try:
        ancestor_role = indicator.find_element(By.XPATH, "./ancestor::div[@role='row']")
        print(f"  Found by role='row': {ancestor_role.get_attribute('class')}")
    except Exception as e:
        print(f"  Ancestor role error: {e}")
    
    # Method 6: Get all divs and check
    all_divs = driver.find_elements(By.XPATH, "//div")
    print(f"  Total divs on page: {len(all_divs)}")

print("\n" + "="*60)
print("FINDING CHAT NAMES")
print("="*60)

# Try to find chat names directly
chat_names = driver.find_elements(By.CSS_SELECTOR, "span[title]")
print(f"Found {len(chat_names)} chat names")
for name in chat_names[:5]:
    print(f"  Chat name: {name.get_attribute('title')}")

input("\nPress Enter to close...")
driver.quit()
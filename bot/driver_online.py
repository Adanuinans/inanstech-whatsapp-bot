# bot/driver.py
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import WHATSAPP_WEB_URL
import os
import time
import tempfile
import shutil


def launch_browser_headless():
    """Launch Firefox in headless mode for Railway/Render deployment"""
    print("🚀 Starting Firefox in headless mode...")
    
    options = Options()
    
    # Headless mode (no UI)
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # Use a temporary profile
    temp_profile = tempfile.mkdtemp(prefix="firefox_profile_")
    options.add_argument(f"-profile")
    options.add_argument(temp_profile)
    
    # Disable unnecessary features
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", False)
    options.set_preference("browser.startup.page", 0)
    options.set_preference("browser.tabs.warnOnClose", False)
    options.set_preference("browser.warnOnQuit", False)
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    
    try:
        service = Service(executable_path="geckodriver")
        driver = webdriver.Firefox(service=service, options=options)
        driver.get(WHATSAPP_WEB_URL)
        print("✅ Firefox launched successfully in headless mode")
        return driver
    except Exception as e:
        print(f"Error launching Firefox headless: {e}")
        try:
            shutil.rmtree(temp_profile, ignore_errors=True)
        except:
            pass
        return None


def is_whatsapp_connected(driver):
    """Check if WhatsApp Web is already connected"""
    if not driver:
        return False
    try:
        driver.find_element(By.CSS_SELECTOR, "div[role='row']")
        return True
    except:
        return False


def get_qr_code(driver):
    """Get QR code as base64 image"""
    if not driver:
        return None
    
    try:
        if is_whatsapp_connected(driver):
            return None
            
        qr_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "canvas[aria-label='QR code']"))
        )
        
        canvas_data = driver.execute_script("return arguments[0].toDataURL('image/png');", qr_element)
        print(f"✅ QR code captured! Length: {len(canvas_data)}")
        return canvas_data
    except Exception as e:
        print(f"QR capture error: {e}")
        return None


def wait_for_connection(driver, timeout=60):
    """Wait for WhatsApp Web connection"""
    print("\n📱 Waiting for WhatsApp connection...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if is_whatsapp_connected(driver):
            print("\n✅ WhatsApp Web connected successfully!")
            return True
        
        elapsed = int(time.time() - start_time)
        print(f"\r⏳ Waiting for scan... {elapsed}s", end="")
        time.sleep(2)
    
    print("\n❌ Connection timeout")
    return False

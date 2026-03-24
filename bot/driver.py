# bot/driver.py
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import FIREFOX_PROFILE_PATH, WHATSAPP_WEB_URL
import os
import time
import tempfile
import shutil
import base64
import io
from PIL import Image

# Add your Firefox binary path
FIREFOX_BINARY_PATH = r"C:\Program Files\Mozilla Firefox\firefox.exe"

# Global driver reference
_driver = None
_current_qr = None


def launch_browser():
    """Launch Firefox for local development (with GUI)"""
    options = Options()
    
    # Set Firefox binary path if exists
    if os.path.exists(FIREFOX_BINARY_PATH):
        options.binary_location = FIREFOX_BINARY_PATH
    
    # Use the existing profile
    options.add_argument(f"--profile={FIREFOX_PROFILE_PATH}")
    
    service = Service(executable_path="geckodriver.exe")
    driver = webdriver.Firefox(service=service, options=options)
    driver.get(WHATSAPP_WEB_URL)
    
    # Wait for user to scan QR code
    input("If WhatsApp asks for QR scan, scan it now and press Enter...")
    return driver


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
        # Try to find geckodriver in system path
        service = Service(executable_path="geckodriver")
        driver = webdriver.Firefox(service=service, options=options)
        driver.get(WHATSAPP_WEB_URL)
        print("✅ Firefox launched successfully in headless mode")
        return driver
    except Exception as e:
        print(f"Error launching Firefox headless: {e}")
        # Clean up temp profile
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
        # First check if already logged in
        if is_whatsapp_connected(driver):
            return None
            
        # Wait for QR code element
        qr_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "canvas[aria-label='QR code']"))
        )
        
        # Get canvas data
        canvas_data = driver.execute_script("return arguments[0].toDataURL('image/png');", qr_element)
        
        # Print QR code data to logs for debugging
        print(f"✅ QR code captured! Data length: {len(canvas_data)}")
        print(f"QR code starts with: {canvas_data[:100]}...")
        
        return canvas_data
    except Exception as e:
        print(f"QR capture error: {e}")
        return None


def print_qr_in_terminal(qr_data):
    """Print QR code as ASCII in terminal"""
    if not qr_data:
        return
    
    # Remove data:image/png;base64, prefix
    if qr_data.startswith('data:image/png;base64,'):
        qr_data = qr_data.split(',')[1]
    
    # Decode base64 to image
    img_data = base64.b64decode(qr_data)
    img = Image.open(io.BytesIO(img_data))
    
    # Convert to ASCII
    img = img.convert('L')
    img = img.resize((50, 50))
    
    chars = "█▓▒░ "
    ascii_art = []
    for y in range(img.height):
        line = ""
        for x in range(img.width):
            pixel = img.getpixel((x, y))
            index = min(len(chars)-1, pixel // (256 // len(chars)))
            line += chars[index]
        ascii_art.append(line)
    
    print("\n" + "="*60)
    print("📱 SCAN THIS QR CODE WITH WHATSAPP:")
    print("="*60)
    for line in ascii_art:
        print(line)
    print("="*60)
    print("Open WhatsApp → Settings → Linked Devices → Link a Device")
    print("="*60 + "\n")


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


def launch_and_connect():
    """Launch browser and wait for connection"""
    driver = launch_browser_headless()
    time.sleep(5)
    
    # Check if already connected
    if is_whatsapp_connected(driver):
        print("✅ Already connected to WhatsApp!")
        return driver
    
    # Get and display QR code
    qr_data = get_qr_code(driver)
    if qr_data:
        print_qr_in_terminal(qr_data)
    else:
        print("⚠️ Could not get QR code. Check if WhatsApp Web loaded properly.")
        # Try to refresh and get QR again
        driver.refresh()
        time.sleep(5)
        qr_data = get_qr_code(driver)
        if qr_data:
            print_qr_in_terminal(qr_data)
    
    # Wait for scan
    if wait_for_connection(driver):
        return driver
    else:
        return None


def get_driver():
    """Get current driver instance"""
    return _driver


def set_driver(driver):
    """Set current driver instance"""
    global _driver
    _driver = driver


def set_qr_code(qr_data):
    """Set current QR code"""
    global _current_qr
    _current_qr = qr_data


def get_qr_code_cached():
    """Get cached QR code"""
    return _current_qr

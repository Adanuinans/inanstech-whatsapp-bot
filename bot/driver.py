from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from config import FIREFOX_PROFILE_PATH, WHATSAPP_WEB_URL

# Add your Firefox binary path
FIREFOX_BINARY_PATH = r"C:\Program Files\Mozilla Firefox\firefox.exe"

def launch_browser():
    options = Options()
    options.binary_location = FIREFOX_BINARY_PATH
    options.add_argument(f"--profile={FIREFOX_PROFILE_PATH}")

    service = Service(executable_path="geckodriver.exe")
    driver = webdriver.Firefox(service=service, options=options)
    driver.get(WHATSAPP_WEB_URL)

    # Wait a few seconds for page load
    input("If WhatsApp asks for QR scan, scan it now and press Enter...")
    return driver
# keep_alive.py
import requests
import time
import os

URL = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:5000')

def keep_alive():
    while True:
        try:
            requests.get(f"{URL}/api/status", timeout=10)
            print("Keep-alive ping sent")
        except:
            print("Keep-alive failed")
        time.sleep(300)  # Every 5 minutes

if __name__ == "__main__":
    keep_alive()
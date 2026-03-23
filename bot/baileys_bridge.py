# bot/baileys_bridge.py
import requests
import time
from threading import Thread

class BaileysBridge:
    def __init__(self, bridge_url="http://localhost:3001"):
        self.bridge_url = bridge_url
        self.connected = False
        self.callback = None
        self.last_message_count = 0
    
    def get_qr(self):
        try:
            response = requests.get(f"{self.bridge_url}/api/qr", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def get_status(self):
        try:
            response = requests.get(f"{self.bridge_url}/api/status", timeout=2)
            if response.status_code == 200:
                self.connected = response.json().get('connected', False)
                return self.connected
        except:
            pass
        return False
    
    def send_message(self, to, message):
        try:
            response = requests.post(f"{self.bridge_url}/api/send",
                                    json={"to": to, "message": message},
                                    timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def set_message_callback(self, callback):
        self.callback = callback
    
    def poll_messages(self, interval=2):
        def poll():
            last_count = 0
            while True:
                try:
                    response = requests.get(f"{self.bridge_url}/api/messages", timeout=5)
                    if response.status_code == 200:
                        messages = response.json()
                        if len(messages) > last_count:
                            for msg in messages[last_count:]:
                                if msg.get('type') == 'incoming' and self.callback:
                                    self.callback(msg.get('from'), msg.get('text'))
                            last_count = len(messages)
                except:
                    pass
                time.sleep(interval)
        
        Thread(target=poll, daemon=True).start()
    
    def wait_for_connection(self, timeout=120):
        print("\n📱 Waiting for WhatsApp connection...")
        print("   QR code will appear in the Render logs")
        print("   Open WhatsApp → Settings → Linked Devices → Link a Device")
        print("   Scan the QR code\n")
        
        start_time = time.time()
        while not self.get_status() and time.time() - start_time < timeout:
            time.sleep(2)
            print(".", end="", flush=True)
        
        if self.get_status():
            print("\n✅ WhatsApp connected successfully!")
            return True
        else:
            print("\n❌ Connection timeout")
            return False

bridge = BaileysBridge()
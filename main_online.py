# main_online.py
import os
import time
import threading
from flask import Flask, render_template, jsonify
from bot.driver import launch_browser_headless, is_whatsapp_connected, get_qr_code, wait_for_connection
from bot.state_manager import StateManager
from bot.router import Router
from bot.simple_watcher import watch_messages

app = Flask(__name__)

driver = None
qr_code = None
is_connected = False

def start_browser():
    global driver, qr_code, is_connected
    print("🚀 Starting Firefox in headless mode...")
    driver = launch_browser_headless()
    
    if not driver:
        print("❌ Failed to start browser")
        return
    
    print("✅ Browser started, waiting for WhatsApp...")
    
    # Wait for QR code to appear
    for i in range(60):
        if is_whatsapp_connected(driver):
            is_connected = True
            print("✅ WhatsApp connected!")
            break
        
        qr_code = get_qr_code(driver)
        if qr_code:
            print("✅ QR code captured")
            break
        time.sleep(2)
    
    if not is_connected and qr_code:
        print("📱 QR code ready. Waiting for scan...")
        # Wait for connection
        if wait_for_connection(driver):
            is_connected = True
            print("✅ WhatsApp connected!")

def run_bot():
    global driver, is_connected
    while True:
        if is_connected and driver:
            try:
                state = StateManager()
                router = Router(state)
                watch_messages(driver, router, state)
            except Exception as e:
                print(f"Bot error: {e}")
        time.sleep(5)

@app.route('/')
def index():
    return render_template('online_dashboard.html', connected=is_connected)

@app.route('/api/qr')
def get_qr_api():
    global qr_code, is_connected
    if is_connected:
        return jsonify({'connected': True})
    elif qr_code:
        return jsonify({'qr': qr_code, 'connected': False})
    else:
        return jsonify({'connected': False})

@app.route('/api/status')
def status():
    return jsonify({'connected': is_connected})

if __name__ == '__main__':
    # Start browser in background
    browser_thread = threading.Thread(target=start_browser)
    browser_thread.start()
    
    # Start bot in background
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Start web server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

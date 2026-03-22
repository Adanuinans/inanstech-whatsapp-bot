# main_online.py
import os
import time
import threading
from flask import Flask, render_template, jsonify
from bot.driver_online import launch_browser, is_whatsapp_connected, get_qr_code
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
    driver = launch_browser()
    
    if not driver:
        print("❌ Failed to start browser")
        return
    
    print("✅ Browser started, waiting for WhatsApp...")
    
    for i in range(60):  # Wait up to 2 minutes
        if is_whatsapp_connected(driver):
            is_connected = True
            print("✅ WhatsApp connected!")
            break
        qr_code = get_qr_code(driver)
        if qr_code:
            print("✅ QR code generated")
        time.sleep(2)
    
    if not is_connected:
        print("⚠️ Waiting for QR scan...")

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
def get_qr():
    if qr_code:
        return jsonify({'qr': qr_code, 'connected': is_connected})
    return jsonify({'qr': None, 'connected': is_connected})

@app.route('/api/status')
def status():
    return jsonify({'connected': is_connected})

def keep_alive():
    """Keep the server alive by pinging itself"""
    import requests
    while True:
        try:
            url = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:5000')
            requests.get(f"{url}/api/status", timeout=5)
            print("Keep-alive ping sent")
        except:
            pass
        time.sleep(300)  # Every 5 minutes

if __name__ == '__main__':
    # Start browser in background
    browser_thread = threading.Thread(target=start_browser)
    browser_thread.start()
    
    # Start bot in background
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Start keep-alive if on Render
    if os.environ.get('RENDER'):
        alive_thread = threading.Thread(target=keep_alive, daemon=True)
        alive_thread.start()
    
    # Start web server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
# bot/followup.py
import time
import json
import os
import re
import random
from datetime import datetime, timedelta
from threading import Thread
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from config import DATA_FOLDER

class FollowUpManager:
    """Manages follow-up messages for inactive chats"""
    
    def __init__(self, driver, state, router):
        self.driver = driver
        self.state = state
        self.router = router
        self.followup_file = os.path.join(DATA_FOLDER, "followup.json")
        self.followup_data = self.load_followup_data()
        self.last_check_time = time.time()
        self.running = True
        self.check_interval = 3600  # Check every hour
        
    def load_followup_data(self):
        """Load followup data from JSON file"""
        try:
            with open(self.followup_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_followup_data(self):
        """Save followup data to JSON file"""
        os.makedirs(DATA_FOLDER, exist_ok=True)
        with open(self.followup_file, 'w', encoding='utf-8') as f:
            json.dump(self.followup_data, f, indent=2, ensure_ascii=False)
    
    def record_interaction(self, chat_id, chat_name, message_sent=False):
        """
        Record when a user interacted or when we sent a message.
        message_sent: True if this was a bot message, False if user message
        """
        now = datetime.now().isoformat()
        
        if chat_id not in self.followup_data:
            self.followup_data[chat_id] = {
                'name': chat_name,
                'last_user_message': None,
                'last_bot_message': None,
                'last_followup_sent': None,
                'interaction_count': 0
            }
        
        if message_sent:
            # This is a bot message
            self.followup_data[chat_id]['last_bot_message'] = now
        else:
            # This is a user message
            self.followup_data[chat_id]['last_user_message'] = now
            self.followup_data[chat_id]['interaction_count'] += 1
        
        self.followup_data[chat_id]['name'] = chat_name
        self.save_followup_data()
    
    def get_chats_needing_followup(self, days_inactive=30):
        """
        Get chats that need a follow-up message.
        Conditions:
        1. Last bot message was more than days_inactive ago
        2. No follow-up sent in the last days_inactive days
        3. There was at least one user interaction before
        """
        inactive_chats = []
        now = datetime.now()
        
        for chat_id, data in self.followup_data.items():
            try:
                # Skip if no bot message ever (never interacted)
                if not data.get('last_bot_message'):
                    continue
                
                # Skip if no user message ever
                if not data.get('last_user_message'):
                    continue
                
                # Check last bot message date
                last_bot = datetime.fromisoformat(data['last_bot_message'])
                days_since_bot = (now - last_bot).days
                
                # Check if followup was already sent recently
                last_followup = data.get('last_followup_sent')
                if last_followup:
                    last_followup_date = datetime.fromisoformat(last_followup)
                    days_since_followup = (now - last_followup_date).days
                    if days_since_followup < days_inactive:
                        continue
                
                # If bot message is older than inactive period, need followup
                if days_since_bot >= days_inactive:
                    inactive_chats.append({
                        'chat_id': chat_id,
                        'name': data['name'],
                        'days_inactive': days_since_bot,
                        'last_bot_message': data['last_bot_message'],
                        'last_user_message': data['last_user_message']
                    })
                    
            except Exception as e:
                print(f"Error checking chat {chat_id}: {e}")
                continue
        
        return inactive_chats
    
    def mark_followup_sent(self, chat_id):
        """Mark that a followup message was sent to this chat"""
        if chat_id in self.followup_data:
            self.followup_data[chat_id]['last_followup_sent'] = datetime.now().isoformat()
            # Also update last_bot_message to reset the timer
            self.followup_data[chat_id]['last_bot_message'] = datetime.now().isoformat()
            self.save_followup_data()
    
    def get_followup_message(self, chat_name):
        """Generate a friendly follow-up message for inactive chats"""
        messages = [
            f"Hi! 👋 It's been a while since we last connected at Inanstech. How's your project coming along? We're still here to help with any web development, mobile apps, or digital marketing needs you might have. 😊",
            
            f"Hello {chat_name}! 🌟 Just checking in - haven't heard from you in a while. Is there anything we can help you with? We're always ready to assist with your tech projects! 🚀",
            
            f"Hey! 👋 Hope you're doing well. Just wanted to reach out and see if you need any help with your website, app, or marketing projects. We'd love to assist! 💡",
            
            f"Hi there! 📱 It's been a month since we last chatted. Just wanted to remind you that Inanstech is here for all your web development, mobile app, and digital marketing needs. Let me know if you'd like to discuss any projects! 🌟",
            
            f"Hello! 👋 At Inanstech, we value our clients and wanted to check in. Have you made any progress on your tech project? We're here to help if you need any support or want to start something new! 🚀",
            
            f"Hi {chat_name}! 😊 Just touching base from Inanstech. We hope everything is going well with your project. If you need any assistance, have questions, or want to discuss new ideas, we're always here to help!"
        ]
        return random.choice(messages)
    
    def send_followup(self, chat_id, chat_name):
        """Send a follow-up message to an inactive chat"""
        try:
            # Find the chat in the sidebar
            chat_found = False
            chat_rows = self.driver.find_elements(By.CSS_SELECTOR, "div[role='row']")
            
            for row in chat_rows:
                try:
                    # Get chat name from the row
                    name_el = row.find_element(By.CSS_SELECTOR, "span[title], div[title]")
                    row_name = name_el.get_attribute("title") or name_el.text.strip()
                    
                    # Normalize both names for comparison
                    from bot.simple_watcher import normalize_chat_name
                    if normalize_chat_name(row_name) == chat_id:
                        chat_found = True
                        # Scroll into view and click
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
                        time.sleep(0.5)
                        ActionChains(self.driver).move_to_element(row).click().perform()
                        time.sleep(1.5)
                        
                        # Generate and send follow-up message
                        followup_text = self.get_followup_message(chat_name)
                        print(f"\n📅 Sending follow-up to {chat_name} (inactive for 30+ days)")
                        
                        # Send the message
                        if self.send_message(followup_text):
                            self.mark_followup_sent(chat_id)
                            print(f"✅ Follow-up sent to {chat_name}")
                            return True
                        break
                except:
                    continue
            
            if not chat_found:
                print(f"⚠️ Could not find chat: {chat_name}")
                return False
                
        except Exception as e:
            print(f"Error sending follow-up to {chat_name}: {e}")
            return False
    
    def send_message(self, reply_text):
        """Send a message using clipboard paste"""
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            selectors = [
                "div[contenteditable='true'][data-tab='10']",
                "div[contenteditable='true'][role='textbox']",
                "div[data-testid='conversation-compose-box'] div[contenteditable='true']",
                "footer div[contenteditable='true'][role='textbox']",
            ]
            
            input_box = None
            for sel in selectors:
                try:
                    input_box = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
                    )
                    if input_box:
                        break
                except:
                    continue
            
            if not input_box:
                return False
            
            input_box.click()
            time.sleep(0.1)
            
            # Clear input
            input_box.send_keys(Keys.CONTROL + "a")
            input_box.send_keys(Keys.DELETE)
            time.sleep(0.05)
            
            # Paste and send
            import pyperclip
            pyperclip.copy(reply_text)
            input_box.send_keys(Keys.CONTROL + "v")
            time.sleep(0.1)
            input_box.send_keys(Keys.ENTER)
            
            return True
            
        except Exception as e:
            print(f"Send failed: {e}")
            return False
    
    def run(self):
        """Background thread to check and send follow-ups"""
        print("📅 Follow-up manager started - checking inactive chats every hour")
        
        while self.running:
            try:
                current_time = time.time()
                
                # Check every hour
                if current_time - self.last_check_time >= self.check_interval:
                    self.last_check_time = current_time
                    
                    # Get chats that need follow-up
                    inactive_chats = self.get_chats_needing_followup(days_inactive=30)
                    
                    if inactive_chats:
                        print(f"\n📅 Found {len(inactive_chats)} inactive chat(s) needing follow-up:")
                        for chat in inactive_chats:
                            print(f"   - {chat['name']} (inactive for {chat['days_inactive']} days)")
                        
                        # Send follow-ups (limit to 3 per hour to avoid spam)
                        for chat in inactive_chats[:3]:
                            self.send_followup(chat['chat_id'], chat['name'])
                            time.sleep(5)  # Wait between messages
                    
            except Exception as e:
                print(f"Follow-up manager error: {e}")
            
            time.sleep(60)  # Check every minute, but only run the check every hour
    
    def stop(self):
        """Stop the follow-up manager thread"""
        self.running = False
        print("📅 Follow-up manager stopped")


def start_followup_manager(driver, state, router):
    """Start the follow-up manager in a background thread"""
    manager = FollowUpManager(driver, state, router)
    thread = Thread(target=manager.run, daemon=True)
    thread.start()
    return manager
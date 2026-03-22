# bot/state_manager.py
import json
import os
from config import USERS_JSON, LEADS_JSON, MESSAGES_JSON, LOGS_JSON, DATA_FOLDER

class StateManager:
    def __init__(self):
        # Ensure data folder exists
        os.makedirs(DATA_FOLDER, exist_ok=True)
        
        self.users_file = USERS_JSON
        self.leads_file = LEADS_JSON
        self.messages_file = MESSAGES_JSON
        self.logs_file = LOGS_JSON
        self.user_states = {}
    
    def load_json(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_user_state(self, phone):
        if phone not in self.user_states:
            self.user_states[phone] = {}
        return self.user_states[phone]
    
    def set_user_state(self, phone, state):
        self.user_states[phone] = state
    
    def save_message(self, phone, msg, incoming=True):
        messages = self.load_json(self.messages_file)
        if phone not in messages:
            messages[phone] = []
        messages[phone].append({"text": msg, "incoming": incoming})
        self.save_json(self.messages_file, messages)

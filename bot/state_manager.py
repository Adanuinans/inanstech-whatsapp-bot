import time

class StateManager:
    def __init__(self):
        self.storage = {}

    def _init_user(self, user_id):
        if user_id not in self.storage:
            self.storage[user_id] = {
                "messages": [],
                "state": {},
                "profile": {}
            }

    def save_message(self, user_id, text, incoming=True):
        self._init_user(user_id)

        self.storage[user_id]["messages"].append({
            "text": text,
            "incoming": incoming,
            "timestamp": time.time()
        })

        # Keep only last 50 messages
        self.storage[user_id]["messages"] = self.storage[user_id]["messages"][-50:]

    def get_conversation_history(self, user_id, limit=10):
        self._init_user(user_id)

        messages = self.storage[user_id]["messages"][-limit:]

        formatted = []
        for msg in messages:
            role = "user" if msg["incoming"] else "assistant"
            formatted.append({
                "role": role,
                "content": msg["text"]
            })

        return formatted

    def get_user_state(self, user_id):
        self._init_user(user_id)
        return self.storage[user_id]["state"]

    def set_user_state(self, user_id, key, value):
        self._init_user(user_id)
        self.storage[user_id]["state"][key] = value

    def get_user_profile(self, user_id):
        self._init_user(user_id)
        return self.storage[user_id]["profile"]

    def set_user_profile(self, user_id, data: dict):
        self._init_user(user_id)
        self.storage[user_id]["profile"].update(data)
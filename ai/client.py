# ai/client.py
import re
import random
from config import MISTRAL_API_KEY

class AIClient:
    def __init__(self):
        print("🤖 AI Client initialized")
        self.mistral_available = False
        
        if MISTRAL_API_KEY:
            try:
                from mistralai.client import MistralClient
                from mistralai.models.chat_completion import ChatMessage
                self.client = MistralClient(api_key=MISTRAL_API_KEY)
                self.model = "mistral-small-latest"
                self.mistral_available = True
                print("✅ Mistral AI initialized")
            except Exception as e:
                print(f"⚠️ Mistral error: {e}")
    
    def generate_reply(self, message):
        if self.mistral_available:
            try:
                from mistralai.models.chat_completion import ChatMessage
                response = self.client.chat(
                    model=self.model,
                    messages=[ChatMessage(role="user", content=message)],
                    temperature=0.7,
                    max_tokens=200
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"AI error: {e}")
        
        # Fallback responses
        msg = message.lower()
        if any(word in msg for word in ["pricing", "price", "cost"]):
            return "Our packages start from ₦100,000 for basic websites, ₦250,000 for e-commerce sites."
        elif any(word in msg for word in ["hello", "hi"]):
            return "Hello! How can I help you with web design, mobile apps, or digital marketing today?"
        else:
            return "Thanks for reaching out! I'm here to help with website design, mobile apps, and digital marketing. What would you like to know?"

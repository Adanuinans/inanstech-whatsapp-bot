# bot/router.py
from engine.menus import MenuEngine
from engine.faq import FAQEngine
from ai.client import AIClient
from bot.state_manager import StateManager
from config import AI_ENABLED

class Router:
    def __init__(self, state: StateManager):
        self.state = state
        self.menu_engine = MenuEngine(state)
        self.faq_engine = FAQEngine(state)
        self.ai_client = AIClient() if AI_ENABLED else None
        print(f"Router initialized - AI Enabled: {AI_ENABLED}")

    def route(self, phone, message):
        print(f"\n{'='*50}")
        print(f"Routing message from {phone}: {message}")
        print(f"{'='*50}")

        # Save incoming message
        self.state.save_message(phone, message, incoming=True)

        # Get user state
        user_state = self.state.get_user_state(phone)
        in_menu_session = user_state.get("stage") in ["menu", "lead_capture"]
        
        # 1. If user is in an active menu session, handle menu first
        if in_menu_session:
            menu_reply = self.menu_engine.get_reply(phone, message)
            if menu_reply:
                print(f"Menu reply: {menu_reply}")
                self.state.save_message(phone, menu_reply, incoming=False)
                return menu_reply
        
        # 2. Check if user wants menu
        if message.lower() in ["menu", "help", "start"]:
            menu_reply = self.menu_engine.get_reply(phone, message)
            if menu_reply:
                print(f"Menu reply: {menu_reply}")
                self.state.save_message(phone, menu_reply, incoming=False)
                return menu_reply
        
        # 3. Use AI for all messages - PASS THE CHAT NAME FOR CONTEXT
        if self.ai_client:
            print("🎯 Using AI for response...")
            # Pass the chat name to maintain conversation context
            ai_reply = self.ai_client.generate_reply(message, phone)
            if ai_reply:
                print(f"AI reply: {ai_reply}")
                self.state.save_message(phone, ai_reply, incoming=False)
                return ai_reply

        # 4. Fallback to FAQ if AI is disabled
        faq_reply = self.faq_engine.get_reply(phone, message)
        if faq_reply:
            print(f"FAQ reply: {faq_reply}")
            self.state.save_message(phone, faq_reply, incoming=False)
            return faq_reply

        # Default response
        default_reply = "Thank you for your message! An agent will get back to you shortly."
        self.state.save_message(phone, default_reply, incoming=False)
        return default_reply
# bot/router.py
from engine.menus import MenuEngine
from engine.faq import FAQEngine
from ai.client import AIClient
from config import AI_ENABLED

class Router:
    def __init__(self, state):
        self.state = state
        self.menu_engine = MenuEngine(state)
        self.faq_engine = FAQEngine(state)
        self.ai_client = AIClient() if AI_ENABLED else None
    
    def route(self, phone, message):
        print(f"Routing message from {phone}: {message}")
        
        # Save message
        self.state.save_message(phone, message, incoming=True)
        
        # Get user state
        user_state = self.state.get_user_state(phone)
        in_menu_session = user_state.get("stage") in ["menu", "lead_capture"]
        
        # Menu first if in session
        if in_menu_session:
            menu_reply = self.menu_engine.get_reply(phone, message)
            if menu_reply:
                self.state.save_message(phone, menu_reply, incoming=False)
                return menu_reply
        
        # Check for menu command
        if message.lower() in ["menu", "help", "start"]:
            menu_reply = self.menu_engine.get_reply(phone, message)
            if menu_reply:
                self.state.save_message(phone, menu_reply, incoming=False)
                return menu_reply
        
        # FAQ
        faq_reply = self.faq_engine.get_reply(phone, message)
        if faq_reply:
            self.state.save_message(phone, faq_reply, incoming=False)
            return faq_reply
        
        # AI
        if self.ai_client:
            ai_reply = self.ai_client.generate_reply(message)
            if ai_reply:
                self.state.save_message(phone, ai_reply, incoming=False)
                return ai_reply
        
        return "Thank you for your message! An agent will get back to you shortly."

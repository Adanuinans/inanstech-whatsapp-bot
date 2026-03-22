# bot/interaction_recorder.py
from bot.followup import FollowUpManager

class InteractionRecorder:
    """Records interactions for follow-up tracking without modifying watcher"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls, driver=None, state=None, router=None):
        if cls._instance is None and driver and state and router:
            cls._instance = FollowUpManager(driver, state, router)
        return cls._instance
    
    @classmethod
    def set_instance(cls, manager):
        """Set the follow-up manager instance"""
        cls._instance = manager
    
    @classmethod
    def record_user_message(cls, chat_id, chat_name):
        if cls._instance:
            cls._instance.record_interaction(chat_id, chat_name, message_sent=False)
    
    @classmethod
    def record_bot_message(cls, chat_id, chat_name):
        if cls._instance:
            cls._instance.record_interaction(chat_id, chat_name, message_sent=True)
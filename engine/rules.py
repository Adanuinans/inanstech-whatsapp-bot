# rules.py
class RulesEngine:
    """
    Contains safety rules and business logic for automated responses
    """
    def __init__(self):
        # Words or patterns that require human intervention
        self.escalation_keywords = ["refund", "urgent", "complaint", "payment", "lawyer", "angry"]

    def requires_human(self, message):
        msg = message.lower()
        return any(keyword in msg for keyword in self.escalation_keywords)
# safety.py
class AISafety:
    """
    Checks AI-generated responses for safety before sending
    """
    prohibited_words = ["discount", "free", "guarantee", "promise", "illegal"]

    def is_safe(self, message):
        msg = message.lower()
        return not any(word in msg for word in self.prohibited_words)
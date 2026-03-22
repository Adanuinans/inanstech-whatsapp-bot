# engine/faq.py
class FAQEngine:
    def __init__(self, state):
        self.state = state
        self.faqs = {
            "pricing": "Our packages start from ₦100,000 for basic websites, ₦250,000 for e-commerce sites.",
            "hours": "We work Monday to Friday, 9AM to 6PM.",
            "portfolio": "https://www.inanstech.com.ng/portfolio",
            "contact": "info@inanstech.com.ng or +234 123 456 7890"
        }
    
    def get_reply(self, phone, message):
        msg = message.lower()
        for key, reply in self.faqs.items():
            if key in msg:
                return reply
        return None

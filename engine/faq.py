# engine/faq.py
class FAQEngine:
    """
    Handles rule-based FAQ responses
    """

    def __init__(self, state):
        self.state = state
        self.faqs = {
            "pricing": "Our packages start from ₦100,000. Contact us for a detailed quote.",
            "price": "Our packages start from ₦100,000. Contact us for a detailed quote.",
            "cost": "Our packages start from ₦100,000. Contact us for a detailed quote.",
            "hours": "We work Monday to Friday, 9AM to 6PM.",
            "opening": "We work Monday to Friday, 9AM to 6PM.",
            "time": "We work Monday to Friday, 9AM to 6PM.",
            "portfolio": "You can see our portfolio here: https://www.inanstech.com.ng/portfolio",
            "work": "You can see our portfolio here: https://www.inanstech.com.ng/portfolio",
            "contact": "You can contact us at info@inanstech.com.ng",
            "email": "You can contact us at info@inanstech.com.ng",
            "phone": "You can contact us at +234 123 456 7890",
            "whatsapp": "You can reach us on WhatsApp at +234 123 456 7890",
            "website": "Visit our website: https://www.inanstech.com.ng",
            "services": "We offer Website Design, Mobile Apps, Software Development, Digital Marketing, E-commerce, and Branding. Reply with 'menu' to see all options.",
            "process": "Our process includes: 1) Consultation, 2) Planning, 3) Design, 4) Development, 5) Testing, 6) Launch, and 7) Support.",
            "maintenance": "Yes, we offer ongoing maintenance and support packages. Our plans start from ₦50,000/year."
        }

    def get_reply(self, user_id, message):
        """
        Check if message matches any FAQ
        """
        clean_message = (message or "").strip()
        msg = clean_message.lower()

        print(f"FAQEngine checking message: {msg}")

        user_state = self.state.get_user_state(user_id)
        if user_state.get("stage") in ["menu", "lead_capture"]:
            print("User in menu flow, skipping FAQ")
            return None

        for key, reply in self.faqs.items():
            if key in msg:
                print(f"FAQ matched: {key}")
                return reply

        print("No FAQ match found")
        return None
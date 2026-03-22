# lead_capture.py
class LeadCaptureEngine:
    """
    Handles structured lead capture questions
    """
    def __init__(self, state):
        self.state = state
        self.questions = [
            "Please provide your full name:",
            "Please provide your business name:",
            "Describe your project/type of service needed:",
            "What is your budget range?",
            "Preferred timeline for completion:"
        ]

    def get_next_question(self, phone):
        user_state = self.state.get_user_state(phone)
        answers = user_state.get("lead_answers", [])
        if len(answers) < len(self.questions):
            return self.questions[len(answers)]
        else:
            # Lead complete
            lead_data = {
                "name": user_state.get("lead_answers", [])[0],
                "business_name": user_state.get("lead_answers", [])[1],
                "project": user_state.get("lead_answers", [])[2],
                "budget": user_state.get("lead_answers", [])[3],
                "timeline": user_state.get("lead_answers", [])[4],
            }
            self.state.add_lead(phone, lead_data)
            user_state["stage"] = "menu"  # reset stage
            self.state.set_user_state(phone, user_state)
            return "Thank you! Your details have been recorded. Our team will contact you soon."
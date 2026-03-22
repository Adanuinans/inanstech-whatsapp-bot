# engine/menus.py
class MenuEngine:
    def __init__(self, state):
        self.state = state
        self.menu_options = {
            "1": "Website Design",
            "2": "Mobile App Development",
            "3": "Software Development",
            "4": "Digital Marketing",
            "5": "E-commerce Solutions",
            "6": "Branding & Design",
            "7": "Pricing / Packages",
            "8": "Portfolio",
            "9": "Talk to an Agent"
        }
    
    def get_reply(self, phone, message):
        user_state = self.state.get_user_state(phone)
        
        if user_state.get("stage") == "menu":
            if message in self.menu_options:
                user_state["selected_service"] = self.menu_options[message]
                user_state["stage"] = "lead_capture"
                self.state.set_user_state(phone, user_state)
                return f"You selected: {self.menu_options[message]}. Please provide your name and contact details."
            else:
                return "Please choose a valid option (1-9)."
        
        if "stage" not in user_state:
            user_state["stage"] = "menu"
            self.state.set_user_state(phone, user_state)
            menu_text = "Hello! Welcome to Inanstech. Please choose:\n"
            for key, val in self.menu_options.items():
                menu_text += f"{key}. {val}\n"
            return menu_text
        
        if user_state.get("stage") == "lead_capture":
            user_state["stage"] = "completed"
            self.state.set_user_state(phone, user_state)
            return "Thank you! We'll contact you shortly."
        
        return None

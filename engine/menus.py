class MenuEngine:
    """
    Handles structured menu options for the bot
    """

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

    def get_reply(self, user_id, message):
        clean_message = (message or "").strip()
        lower_message = clean_message.lower()

        print(f"MenuEngine processing message: {clean_message} from {user_id}")

        user_state = self.state.get_user_state(user_id)
        print(f"Current user state: {user_state}")

        if lower_message in ["menu", "help", "start"]:
            user_state["stage"] = "menu"
            user_state.pop("selected_service", None)
            user_state.pop("lead_details", None)
            self.state.set_user_state(user_id, user_state)
            return self.show_menu()

        if user_state.get("stage") == "menu":
            if clean_message in self.menu_options:
                selected_service = self.menu_options[clean_message]
                user_state["selected_service"] = selected_service
                user_state["stage"] = "lead_capture"
                self.state.set_user_state(user_id, user_state)

                return (
                    f"You selected: {selected_service}.\n\n"
                    f"Please send your name and contact details so we can reach out to you."
                )
            else:
                return "Please choose a valid option from 1 to 9."

        if user_state.get("stage") == "lead_capture":
            user_state["lead_details"] = clean_message
            user_state["stage"] = "completed"
            self.state.set_user_state(user_id, user_state)

            self.state.save_lead(
                user_id,
                clean_message,
                user_state.get("selected_service", "Unknown"),
                {"details": clean_message}
            )

            return (
                f"Thank you for your interest in {user_state.get('selected_service', 'our service')}.\n\n"
                f"We've received your details and a representative will contact you shortly."
            )

        if user_state.get("stage") == "completed":
            if lower_message in ["menu", "help", "start"]:
                user_state["stage"] = "menu"
                user_state.pop("selected_service", None)
                user_state.pop("lead_details", None)
                self.state.set_user_state(user_id, user_state)
                return self.show_menu()
            return None

        return None

    def show_menu(self):
        menu_text = "📋 *Main Menu*\n\n"
        for key, val in self.menu_options.items():
            menu_text += f"{key}. {val}\n"
        menu_text += "\nReply with the number of your choice."
        return menu_text
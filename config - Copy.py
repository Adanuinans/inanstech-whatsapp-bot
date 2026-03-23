# config.py
import os

WHATSAPP_WEB_URL = "https://web.whatsapp.com/"
FIREFOX_PROFILE_PATH = r"C:\Users\Adams\AppData\Roaming\Mozilla\Firefox\Profiles\2ozw1a8d.WhatsappBot"

DATA_FOLDER = os.path.join(os.getcwd(), "data")
USERS_JSON = os.path.join(DATA_FOLDER, "users.json")
LEADS_JSON = os.path.join(DATA_FOLDER, "leads.json")
MESSAGES_JSON = os.path.join(DATA_FOLDER, "messages.json")
LOGS_JSON = os.path.join(DATA_FOLDER, "logs.json")
FAQ_JSON = os.path.join(DATA_FOLDER, "faq.json")
MENU_JSON = os.path.join(DATA_FOLDER, "menu.json")
SETTINGS_JSON = os.path.join(DATA_FOLDER, "settings.json")

# Mistral AI Configuration
MISTRAL_API_KEY = ""
MISTRAL_MODEL = "mistral-small-latest"  # Free tier model

# Other AI keys (optional)
HUGGINGFACE_API_KEY = ""
GEMINI_API_KEY = ""
OPENAI_API_KEY = ""

# AI Settings
AI_ENABLED = True

# config.py
import os

# WhatsApp Web URL
WHATSAPP_WEB_URL = "https://web.whatsapp.com/"

# Data folder
DATA_FOLDER = os.path.join(os.getcwd(), "data")
USERS_JSON = os.path.join(DATA_FOLDER, "users.json")
LEADS_JSON = os.path.join(DATA_FOLDER, "leads.json")
MESSAGES_JSON = os.path.join(DATA_FOLDER, "messages.json")
LOGS_JSON = os.path.join(DATA_FOLDER, "logs.json")
FAQ_JSON = os.path.join(DATA_FOLDER, "faq.json")
MENU_JSON = os.path.join(DATA_FOLDER, "menu.json")
SETTINGS_JSON = os.path.join(DATA_FOLDER, "settings.json")

# Mistral AI Configuration
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "")
MISTRAL_MODEL = "mistral-small-latest"

# AI Settings
AI_ENABLED = True
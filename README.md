# Inanstech WhatsApp Bot

AI-powered WhatsApp bot for customer service, lead generation, and automated responses.

## Features

- 🤖 AI-powered responses using Mistral AI
- 📱 WhatsApp Web integration
- 📊 Dashboard for monitoring
- 🔗 QR code pairing
- 📈 Lead capture and tracking
- 📝 Conversation history
- 🔄 Auto-followup for inactive chats

## Deployment

This bot is designed to be deployed on Render.com.

### Environment Variables

Set these in Render dashboard:

- `MISTRAL_API_KEY`: Your Mistral AI API key
- `PYTHON_VERSION`: 3.11.0

### Local Development

```bash
pip install -r requirements.txt
python main_online.py
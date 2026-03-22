# test_mistral.py
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

API_KEY = "d3g94JPrb9GTfBKwz3KVRgQvXT4XkfqO"

print("Testing Mistral API Key...")
print(f"Key: {API_KEY[:10]}...")

try:
    client = MistralClient(api_key=API_KEY)
    
    response = client.chat(
        model="mistral-small-latest",
        messages=[
            ChatMessage(role="user", content="Say 'Hello! Mistral AI is working!'")
        ],
        max_tokens=30
    )
    
    print("✅ API Key is VALID!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ API Key Error: {e}")
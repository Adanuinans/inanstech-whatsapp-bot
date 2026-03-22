# ai/client.py
import re
import random
import math
import time
from datetime import datetime
from config import MISTRAL_API_KEY

class AIClient:
    def __init__(self):
        print("🤖 AI Client initialized")
        
        # Initialize Mistral AI
        self.mistral_available = False
        self.conversation_history = {}  # Store conversation history per chat
        
        print(f"🔑 Checking Mistral API Key: {MISTRAL_API_KEY[:10] if MISTRAL_API_KEY else 'None'}...")
        
        if MISTRAL_API_KEY and MISTRAL_API_KEY != "" and MISTRAL_API_KEY != "DWYRgnxjlcBMzmva7dd0SPp4RHqh5suE":
            try:
                from mistralai.client import MistralClient
                from mistralai.models.chat_completion import ChatMessage
                
                self.client = MistralClient(api_key=MISTRAL_API_KEY)
                self.model = "mistral-small-latest"
                self.mistral_available = True
                print("  ✅ Mistral AI initialized successfully!")
                print(f"  📊 Model: {self.model}")
                print("  🎯 Free tier: 500k tokens/min")
            except ImportError:
                print("  ⚠️ Mistral package not installed. Run: pip install mistralai")
            except Exception as e:
                print(f"  ⚠️ Mistral initialization error: {e}")
        else:
            print("  ⚠️ No valid Mistral API key found - using rule-based only")
            print("  💡 To use Mistral AI:")
            print("     1. Sign up at https://console.mistral.ai")
            print("     2. Get your API key")
            print("     3. Add it to config.py")
        
        print("✅ AI Client ready - With conversation memory")
    
    def get_conversation_context(self, chat_name, max_messages=6):
        """Get recent conversation history for context"""
        if chat_name not in self.conversation_history:
            return []
        return self.conversation_history[chat_name][-max_messages:]
    
    def add_to_history(self, chat_name, role, message):
        """Add a message to conversation history"""
        if chat_name not in self.conversation_history:
            self.conversation_history[chat_name] = []
        
        self.conversation_history[chat_name].append({
            'role': role,
            'message': message,
            'timestamp': time.time()
        })
        
        # Keep only last 30 messages
        if len(self.conversation_history[chat_name]) > 30:
            self.conversation_history[chat_name] = self.conversation_history[chat_name][-30:]
    
    def generate_reply(self, message, chat_name="Unknown"):
        """Generate intelligent response using AI with conversation context"""
        
        # Add user message to history
        self.add_to_history(chat_name, 'user', message)
        
        # Get conversation context
        history = self.get_conversation_context(chat_name, max_messages=8)
        
        # Try Mistral AI first
        if self.mistral_available:
            try:
                print("🎯 Generating with Mistral AI...")
                response = self.generate_mistral_with_context(message, chat_name, history)
                if response:
                    print("✅ Mistral AI response received!")
                    self.add_to_history(chat_name, 'assistant', response)
                    return response
                else:
                    print("⚠️ No response from Mistral, using fallback")
            except Exception as e:
                print(f"⚠️ Mistral error: {e}")
        
        # Fallback to rule-based with context
        print("🎯 Using rule-based fallback")
        response = self.rule_based_with_context(message, history, chat_name)
        self.add_to_history(chat_name, 'assistant', response)
        return response
    
    def generate_mistral_with_context(self, message, chat_name, history):
        """Generate response using Mistral AI with conversation context"""
        try:
            from mistralai.client import MistralClient
            from mistralai.models.chat_completion import ChatMessage
            
            # Build conversation messages with context
            messages = [
                ChatMessage(role="system", content="""You are a friendly, helpful AI assistant for Inanstech, a Nigerian technology company.

COMPANY SERVICES:
- Website Design & Development: Starting from N100,000 (basic), N250,000 (e-commerce)
- Mobile App Development: Starting from N500,000 (Android & iOS)
- Custom Software Development: Custom quotes based on requirements
- Digital Marketing: From N150,000/month (SEO, social media, ads)
- E-commerce Solutions: Custom online stores with payment integration
- Branding & Design: Logo, identity design packages

IMPORTANT CONVERSATION RULES:
1. REMEMBER what was discussed earlier in the conversation
2. Reference previous messages naturally when relevant
3. If the user asks a follow-up question, connect it to what was said before
4. Be consistent with information you've already shared
5. Keep track of what the user is interested in (e.g., website, app, pricing, timeline)
6. Answer naturally as if you remember the whole conversation

YOUR PERSONALITY:
- Be friendly, warm, and professional
- Keep responses concise but helpful (2-4 sentences)
- Use emojis occasionally 😊
- Always be helpful and solution-oriented
- If asked about pricing, mention the starting prices above
- If asked about contact, share info@inanstech.com.ng and +234 123 456 7890""")
            ]
            
            # Add conversation history
            for hist in history[-6:]:
                role = "user" if hist['role'] == 'user' else "assistant"
                messages.append(ChatMessage(role=role, content=hist['message']))
            
            # Add current message
            if not history or history[-1]['message'] != message:
                messages.append(ChatMessage(role="user", content=message))
            
            # Make the API call
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=250
            )
            
            reply = response.choices[0].message.content.strip()
            if reply:
                print(f"🤖 Mistral: {reply[:100]}...")
                return reply
            return None
            
        except Exception as e:
            print(f"Mistral generation error: {e}")
            return None
    
    def rule_based_with_context(self, message, history, chat_name):
        """Enhanced rule-based that uses conversation context"""
        msg = message.lower()
        
        # Extract key information from history to understand context
        previous_messages = []
        previous_topics = []
        for hist in history[-6:]:
            previous_messages.append(hist['message'].lower())
            if hist['role'] == 'user':
                previous_topics.append(hist['message'].lower())
        
        # Detect conversation topics from history
        discussing_pricing = any('price' in p or 'cost' in p or 'how much' in p or 'expensive' in p for p in previous_topics)
        discussing_website = any('website' in p or 'web' in p or 'site' in p for p in previous_topics)
        discussing_app = any('app' in p or 'mobile' in p or 'android' in p or 'ios' in p for p in previous_topics)
        discussing_timeline = any('timeline' in p or 'how long' in p or 'month' in p or 'week' in p or 'duration' in p for p in previous_topics)
        discussing_compare = any('compare' in p or 'difference' in p or 'vs' in p or 'versus' in p for p in previous_topics)
        
        # Check if this is a follow-up to a previous conversation
        is_followup = len(history) > 2 and any(hist['role'] == 'user' for hist in history[-3:])
        
        # ========== PRICING FOLLOW-UP ==========
        if discussing_pricing and any(word in msg for word in ["expensive", "cost", "price", "affordable", "too much", "high"]):
            if discussing_website:
                return "I understand your concern about the pricing! Our N100,000 basic website package includes a fully responsive design, SEO optimization, contact forms, and 3 months of basic support. We also offer payment plans to make it more manageable. Would you like to see what's included in more detail or discuss a payment plan?"
            elif discussing_app:
                return "I hear you! Our N500,000 app development includes both Android and iOS versions, backend development, and App Store/Play Store deployment. For a basic app with essential features only, we could create a more streamlined version at a lower cost. Would you like to discuss your must-have features?"
            else:
                return "I understand pricing is an important consideration! Our packages are designed to provide excellent value. Would you like me to break down exactly what's included in each package so you can see the value you're getting? We can also discuss payment options."
        
        # ========== TIMELINE FOLLOW-UP ==========
        elif discussing_timeline and any(word in msg for word in ["timeline", "how long", "month", "week", "fast", "quick", "soon"]):
            if discussing_website:
                return "A basic website typically takes 2-3 weeks. For a 1-month timeline, we can definitely accommodate that with a focused development schedule. We'll work with your timeline! Would you like to discuss a specific launch date?"
            elif discussing_app:
                return "A basic app can be completed in 2-3 months. For a 1-month timeline, we would need to focus on core features only and use a simpler tech stack. Let's discuss what features are most important to you - we can prioritize and deliver an MVP first!"
            else:
                return "Project timelines vary based on complexity. A basic website takes 2-3 weeks, while a custom app can take 2-3 months. What's your ideal timeline? We can work within your schedule and prioritize accordingly!"
        
        # ========== COMPARISON FOLLOW-UP ==========
        elif discussing_compare or any(word in msg for word in ["compare", "difference", "vs", "versus", "between"]):
            if discussing_website and discussing_app:
                return "Great question! Let me break down the key differences:\n\n📱 **Website vs App:**\n- Website: Best for online presence, SEO, and reaching customers via browsers (from N100,000)\n- Mobile App: Best for engagement, push notifications, and offline access (from N500,000)\n\nMany businesses start with a website and add an app later. Based on our conversation, what's your primary goal - building an online presence or engaging existing customers?"
            else:
                return "Let me help you compare! What specific services are you interested in comparing? We offer websites (from N100,000), mobile apps (from N500,000), and digital marketing (from N150,000/month). Tell me what you're trying to achieve and I'll recommend the best fit!"
        
        # ========== WEBSITE DESIGN ==========
        elif any(word in msg for word in ["website", "web", "design", "site"]):
            if discussing_timeline:
                return "For a website, we can deliver a professional, responsive site in 2-3 weeks. If you need it faster, let me know your timeline and we'll make it work! Starting from N100,000. What type of website are you looking for?"
            elif discussing_pricing:
                return "Our website packages start from N100,000 (basic) to N250,000 (e-commerce). Both include responsive design and SEO optimization. Would you like to see what's included in each package or discuss a custom option?"
            return "We create modern, responsive websites starting from N100,000. Based on our conversation, it sounds like you're interested in establishing an online presence. What type of website are you looking for? Business site, e-commerce, or blog?"
        
        # ========== MOBILE APPS ==========
        elif any(word in msg for word in ["app", "mobile", "android", "ios", "application"]):
            if discussing_timeline:
                return "Mobile app development typically takes 2-3 months, but we can create a Minimum Viable Product (MVP) in 1-2 months with core features. Starting from N500,000. What's your ideal launch date?"
            elif discussing_pricing:
                return "Our app development starts at N500,000 for both Android and iOS. This includes backend development, UI/UX design, and app store deployment. Would you like to discuss a custom package based on your specific features?"
            return "We develop high-quality mobile apps for Android and iOS starting from N500,000. Based on our conversation, what problem would you like your app to solve? Tell me about your app idea!"
        
        # ========== PRICING QUESTIONS ==========
        elif any(word in msg for word in ["pricing", "price", "cost", "how much", "quote", "fee", "charge"]):
            if discussing_website:
                return "Our website packages:\n• Basic Website: N100,000 (responsive design, SEO, contact form)\n• E-commerce Site: N250,000 (payment integration, product management)\n\nWould you like a custom quote based on your specific requirements?"
            elif discussing_app:
                return "Our app development starts from N500,000 for a basic app with essential features. Custom apps with more features are quoted based on complexity. Would you like to discuss your app idea for a more accurate estimate?"
            else:
                return """Our packages:
• Basic Website: N100,000
• E-commerce Site: N250,000
• Mobile App: from N500,000
• Digital Marketing: from N150,000/month

Want a custom quote based on your specific needs? Tell me about your project!"""
        
        # ========== TIMELINE QUESTIONS ==========
        elif any(word in msg for word in ["timeline", "how long", "duration", "take", "complete"]):
            return "Project timelines vary:\n• Basic Website: 2-3 weeks\n• E-commerce Site: 3-4 weeks\n• Mobile App: 2-3 months\n• Custom Software: 3-6 months\n\nWhat type of project are you considering? I can give you a more specific timeline based on your needs!"
        
        # ========== DIGITAL MARKETING ==========
        elif any(word in msg for word in ["marketing", "seo", "social media", "ads"]):
            return "Our digital marketing packages start from N150,000/month and include SEO, social media management, and targeted ads. Based on our conversation, what's your marketing goal? More website traffic, brand awareness, or leads?"
        
        # ========== CONVERSATIONAL ==========
        elif any(word in msg for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            if any('hello' in h['message'].lower() or 'hi' in h['message'].lower() for h in history[-3:] if h['role'] == 'user'):
                return "Hey again! 😊 How can I help you further with your project? Do you have more questions about our services, pricing, or timeline based on what we discussed?"
            return "Hello! 👋 I'm your Inanstech AI assistant. I can help with websites, mobile apps, software development, and digital marketing. What would you like to know?"
        
        elif any(word in msg for word in ["thank", "thanks", "appreciate"]):
            return "You're very welcome! 😊 Is there anything else you'd like to know about our services? I'm happy to help with pricing, timelines, or project details - especially based on what we discussed!"
        
        elif any(word in msg for word in ["bye", "goodbye", "see you", "later"]):
            return "Thank you for chatting! 😊 Feel free to reach out anytime if you have more questions about websites, apps, or anything we discussed. Have a great day!"
        
        elif "joke" in msg:
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs! 😄 What can we build for you?",
                "What do you call a developer from Nigeria? A Nai-Java programmer! 😂 Want to learn about our services?",
                "Why did the website go to therapy? It had too many issues! 🛠️ We can help fix that - what do you need built?"
            ]
            return random.choice(jokes)
        
        elif any(word in msg for word in ["menu", "help", "services", "what do you do"]):
            return """I can help with:
- Website Design (from N100,000)
- Mobile Apps (from N500,000)
- Software Development
- Digital Marketing (from N150,000/month)
- E-commerce Solutions
- Branding & Design

Based on our conversation, would you like more details about any of these? I can give you pricing, timeline, or feature information!"""
        
        # ========== DEFAULT WITH CONTEXT ==========
        else:
            if "?" in message:
                if discussing_website or discussing_app:
                    return f"Great question! Based on our conversation about {'websites' if discussing_website else 'apps'}, I'd be happy to help. Would you like more details on pricing, timeline, or features? Or would you like a custom quote?"
                else:
                    return f"Great question! At Inanstech, we specialize in turning ideas into digital reality. Based on what we've discussed, would you like more information about our services or would you like a custom quote?"
            else:
                if discussing_website or discussing_app:
                    return f"Thanks for reaching out! I'm here to help with your {'website project' if discussing_website else 'app idea'}. What specific aspect would you like to learn more about - pricing, timeline, or features?"
                else:
                    return f"Thanks for reaching out! I'm here to help with web design, mobile apps, and digital marketing. What would you like to know more about? I can share pricing, timelines, or service details!"
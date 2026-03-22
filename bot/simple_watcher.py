# bot/simple_watcher.py
import time
import re
import random
import pyperclip
from bot.interaction_recorder import InteractionRecorder
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =========================
# DEBUG (CONSOLE)
# =========================
def debug_group_console(driver, chat_display):
    """Print debug info about the current chat to console"""
    print("\n" + "=" * 60)
    print("🔍 GROUP DEBUG (CONSOLE)")
    print("=" * 60)

    print(f"📌 CHAT NAME:\n{chat_display}\n")

    try:
        header = driver.find_element(By.CSS_SELECTOR, "header")
        html = header.get_attribute("innerHTML")

        print("📦 HEADER HTML (first 1500 chars):\n")
        print(html[:1500])

    except Exception as e:
        print(f"❌ Header error: {e}")

    print("=" * 60 + "\n")


def debug_chat_structure(driver, chat_name, log_to_file=True):
    """
    Debug function to log the HTML structure of the current chat.
    This helps identify group vs individual chat patterns.
    """
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Get the chat header
        header = driver.find_element(By.CSS_SELECTOR, "header")
        header_html = header.get_attribute("outerHTML")
        
        # Prepare debug info
        debug_info = f"""
{'='*80}
DEBUG CHAT STRUCTURE - {timestamp}
{'='*80}
CHAT NAME: {chat_name}

--- HEADER STRUCTURE ---
{header_html[:1500]}

--- KEY ATTRIBUTES ---
Header attributes:
- aria-label: {header.get_attribute('aria-label')}
- data-testid: {header.get_attribute('data-testid')}
- role: {header.get_attribute('role')}

Check for group indicators:
- 'group' in header text: {'group' in header.text.lower()}
- 'participants' in header text: {'participants' in header.text.lower()}
- 'members' in header text: {'members' in header.text.lower()}
- Contains multiple names: {header.text.count('+') > 1 or header.text.count(',') > 2}

{'='*80}
"""
        
        print(debug_info)
        
        # Save to file for later analysis
        if log_to_file:
            with open("debug_chat_structure.log", "a", encoding="utf-8") as f:
                f.write(debug_info)
        
        return debug_info
        
    except Exception as e:
        print(f"Debug error: {e}")
        return None


# =========================
# 🔥 STRONG GROUP DETECTION
# =========================
def is_group_chat(driver, chat_display=None):
    """
    Detect if a chat is a group chat using multiple methods.
    Returns True if it's a group, False otherwise.
    """
    try:
        name = (chat_display or "").lower()

        # ✅ CASE 1: WhatsApp group indicator text
        if "group info" in name:
            return True

        # ✅ CASE 2: Many names/numbers (comma separated list)
        if "," in name:
            parts = [p.strip() for p in name.split(",") if p.strip()]
            if len(parts) >= 3:
                return True

        # ✅ CASE 3: Many phone numbers in the name
        numbers = re.findall(r'\+?\d{7,}', name)
        if len(numbers) >= 2:
            return True

        # ✅ CASE 4: Very long name → likely group
        if len(name) > 35:
            return True

        # ✅ CASE 5: Header structure detection
        try:
            header = driver.find_element(By.CSS_SELECTOR, "header")

            # Look for group info button/text
            group_info = header.find_elements(By.XPATH, ".//span[contains(text(), 'group')]")
            if group_info:
                return True

            # Look for multiple selectable participants
            participants = header.find_elements(
                By.CSS_SELECTOR,
                "span[data-testid='selectable-text'][title]"
            )

            for el in participants:
                title = el.get_attribute("title") or ""
                if "," in title or title.count("+") > 1:
                    return True

        except:
            pass

        # ✅ CASE 6: Check HTML structure - groups have direct span, individuals have nested divs
        try:
            # Find the chat row in the sidebar
            chat_rows = driver.find_elements(By.CSS_SELECTOR, "div[role='row']")
            for row in chat_rows:
                try:
                    row_text = row.text
                    if chat_display and chat_display in row_text:
                        name_container = row.find_element(By.CSS_SELECTOR, "div[class*='_ak8q']")
                        
                        # Look for direct span[title] as immediate child of _ak8q
                        direct_span = name_container.find_elements(By.XPATH, "./span[@title]")
                        
                        # Look for nested span inside div structure (individual chats)
                        nested_span = name_container.find_elements(By.XPATH, ".//div[contains(@class, 'x1c4vz4f')]//span[@title]")
                        
                        if direct_span and not nested_span:
                            # Direct span without nested structure = GROUP
                            return True
                        break
                except:
                    continue
        except:
            pass

        return False

    except:
        return False


# =========================
# NORMALIZATION
# =========================
def extract_phone_from_name(name):
    """
    Extract phone number from various name formats.
    """
    if not name:
        return None
    
    phone_pattern = r'[\+]?[\d\s\-\(\)]{8,}'
    matches = re.findall(phone_pattern, name)
    
    if matches:
        phone = matches[0]
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        if phone.startswith('+'):
            return phone
        elif len(phone) >= 10:
            return phone
    
    return None


def normalize_chat_name(name):
    """
    Normalize chat names to a unique identifier.
    """
    if not name:
        return None

    name = name.strip()
    
    # Try to extract phone number
    phone = extract_phone_from_name(name)
    if phone:
        return re.sub(r'\D', '', phone)

    # Handle "Official WhatsApp account"
    if "official whatsapp" in name.lower():
        return "whatsapp_business"

    # Remove common prefixes and special chars
    name = re.sub(r'^\+?\d{1,3}\s*', '', name)
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()

    return name.lower()


# =========================
# GET CURRENT CHAT NAME
# =========================
def get_current_chat_name(driver):
    """Get the name of the currently open chat from the header."""
    selectors = [
        "header span[title]",
        "div[data-testid='conversation-title'] span[title]",
        "header div[title]",
        "header span[dir='auto']",
    ]

    for sel in selectors:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            name = (el.get_attribute("title") or el.text or "").strip()
            if name and name.lower() not in ["", "profile details", "online", "offline", "typing..."]:
                return name
        except:
            continue

    return None


# =========================
# TYPING DETECTION
# =========================
def is_typing(driver):
    """
    Detect WhatsApp Web typing indicator.
    """
    try:
        # Method 1: Look for typing indicator element
        typing_indicators = driver.find_elements(By.CSS_SELECTOR, "[data-testid='typing-indicator']")
        if any(el.is_displayed() for el in typing_indicators):
            return True
        
        # Method 2: Look for typing SVG animation
        svgs = driver.find_elements(By.CSS_SELECTOR, "svg[viewBox='0 0 72 72']")
        for svg in svgs:
            if svg.is_displayed():
                try:
                    parent = svg.find_element(By.XPATH, "./ancestor::div[contains(@class, 'message')]")
                    if parent:
                        return True
                except:
                    pass
                return True
        
        # Method 3: Look for gray circle paths (typing dots)
        paths = driver.find_elements(By.CSS_SELECTOR, "path[fill='rgb(102,119,129)']")
        if len(paths) >= 5:
            return True
        
        # Method 4: Look for typing indicator by text/aria-label
        typing_text = driver.find_elements(By.CSS_SELECTOR, "div[aria-label*='typing'], span[aria-label*='typing']")
        for elem in typing_text:
            if elem.is_displayed():
                return True
        
        return False
        
    except Exception:
        return False


def wait_for_typing_to_stop(driver, max_wait=12):
    """
    Wait for typing indicator to disappear.
    Returns True if typing stopped, False if timeout.
    """
    start = time.time()
    was_typing = False

    while time.time() - start < max_wait:
        if is_typing(driver):
            if not was_typing:
                print("✍️ User is typing... waiting")
                was_typing = True
            time.sleep(0.5)
        else:
            if was_typing:
                print("✍️ User stopped typing")
                return True
            time.sleep(0.3)

    return not is_typing(driver)


# =========================
# WATCHER LOOP
# =========================
def watch_messages(driver, router, state):
    print("=" * 50)
    print("WHATSAPP MESSAGE WATCHER STARTED")
    print("=" * 50)
    print("Waiting for WhatsApp to load...")
    time.sleep(10)
    print("WhatsApp loaded. Monitoring for messages...")

    # Track processed messages with timestamps
    processed_messages = {}      # message_key → timestamp
    last_reply_time = {}         # chat_id → timestamp
    last_processed_text = {}     # chat_id → last message text
    last_message_count = {}      # chat_id → message count
    processing_lock = {}         # chat_id → timestamp (prevent concurrent processing)
    last_sent_message = {}       # chat_id → (timestamp, message_text)
    
    # Debug mode flag
    DEBUG_MODE = True

    while True:
        try:
            current_chat_display = get_current_chat_name(driver)
            current_id = normalize_chat_name(current_chat_display) if current_chat_display else None

            # Clean up old entries
            now = time.time()
            for key in list(processed_messages.keys()):
                if processed_messages[key] < now - 30:
                    del processed_messages[key]

            # Clean up old locks (older than 10 seconds)
            for chat_id in list(processing_lock.keys()):
                if processing_lock[chat_id] < now - 10:
                    del processing_lock[chat_id]
            
            # Clean up old last_sent_message entries (older than 60 seconds)
            for chat_id in list(last_sent_message.keys()):
                if now - last_sent_message[chat_id][0] > 60:
                    del last_sent_message[chat_id]

            # ─── UNREAD CHATS ───────────────────────────────────────────────────
            unread_indicators = driver.find_elements(By.CSS_SELECTOR, "span[aria-label*='unread']")

            if unread_indicators:
                for indicator in unread_indicators:
                    try:
                        # Find the chat row
                        chat_row = None
                        try:
                            chat_row = indicator.find_element(By.XPATH, "./ancestor::div[@role='row']")
                        except:
                            p = indicator
                            for _ in range(7):
                                p = p.find_element(By.XPATH, "..")
                                if p.get_attribute("role") == "row":
                                    chat_row = p
                                    break

                        if not chat_row:
                            continue

                        # Get chat name
                        name_el = None
                        try:
                            name_el = chat_row.find_element(By.CSS_SELECTOR, "span[title], div[title]")
                        except:
                            pass

                        chat_display = name_el.get_attribute("title") or name_el.text.strip() if name_el else None
                        if not chat_display or chat_display in ["Unknown", "Profile details"]:
                            continue

                        chat_id = normalize_chat_name(chat_display)

                        # Skip if already processing
                        if chat_id in processing_lock:
                            continue

                        # Check cooldown
                        if chat_id in last_reply_time and now - last_reply_time[chat_id] < 10:
                            continue

                        print(f"\n📬 Opening unread chat: {chat_display}")

                        # Open the chat
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chat_row)
                        time.sleep(0.6)
                        ActionChains(driver).move_to_element(chat_row).click().perform()
                        time.sleep(2)

                        # DEBUG: Analyze chat structure
                        if DEBUG_MODE:
                            debug_group_console(driver, chat_display)
                            debug_chat_structure(driver, chat_display, log_to_file=True)

                        # Check if it's a group after opening
                        if is_group_chat(driver, chat_display):
                            print(f"🚫 BLOCKED GROUP: {chat_display} - skipping")
                            continue

                        # Process messages
                        process_new_messages(
                            driver, router, state, chat_id, chat_display,
                            processed_messages, last_reply_time, last_processed_text,
                            last_message_count, processing_lock, last_sent_message
                        )

                    except Exception as e:
                        continue

            # ─── CURRENT CHAT ───────────────────────────────────────────────────
            if current_id and current_id not in processing_lock:
                try:
                    # Check if current chat is a group
                    if is_group_chat(driver, current_chat_display):
                        print(f"⏭️ Currently in group chat: {current_chat_display} - skipping")
                        time.sleep(2)
                        continue

                    # Check for new messages
                    incoming_msgs = driver.find_elements(By.CSS_SELECTOR, "div[class*='message-in']")
                    current_count = len(incoming_msgs)
                    prev_count = last_message_count.get(current_id, 0)

                    if current_count > prev_count:
                        process_new_messages(
                            driver, router, state, current_id, current_chat_display,
                            processed_messages, last_reply_time, last_processed_text,
                            last_message_count, processing_lock, last_sent_message
                        )

                    last_message_count[current_id] = current_count

                except Exception as e:
                    print(f"Current chat error: {e}")

            time.sleep(1.5)

        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(5)


# =========================
# PROCESS MESSAGES
# =========================
def process_new_messages(driver, router, state, chat_id, chat_display,
                         processed_messages, last_reply_time, last_processed_text,
                         last_message_count, processing_lock, last_sent_message):
    """
    Process new messages in a chat - ensures only ONE reply per message.
    """
    now = time.time()

    # 🔥 Record that a user message was received (for follow-up tracking)
    InteractionRecorder.record_user_message(chat_id, chat_display)

    # Check if this chat is already being processed
    if chat_id in processing_lock:
        print(f"⏭️ Skipping {chat_display} - already processing")
        return

    # Set processing lock
    processing_lock[chat_id] = now

    try:
        # Double-check it's not a group
        if is_group_chat(driver, chat_display):
            print(f"🚫 BLOCKED GROUP (during processing): {chat_display}")
            return

        # Get all messages in the chat (both incoming and outgoing)
        all_messages = driver.find_elements(By.CSS_SELECTOR, "div[class*='message-in'], div[class*='message-out']")
        
        if not all_messages:
            return
        
        # The last message in the DOM is the newest
        last_message = all_messages[-1]
        last_message_class = last_message.get_attribute("class") or ""
        
        # Check if the last message is from the bot (message-out)
        if "message-out" in last_message_class or "outgoing" in last_message_class:
            print(f"📤 Last message in {chat_display} was from bot - no need to reply")
            return
        
        # If we get here, the last message is from the user (incoming)
        # Now find the latest user message text
        latest_message = None
        for msg in reversed(all_messages):
            try:
                cls = msg.get_attribute("class") or ""
                if "message-out" in cls or "outgoing" in cls:
                    continue
                
                # Skip system messages
                text = msg.text.strip()
                if not text or len(text) < 2:
                    continue
                
                if any(x in text.lower() for x in ["unread messages", "end-to-end encrypted", "whatsapp"]):
                    continue
                
                # Clean text
                text = re.sub(r'\d+:\d+\s*(am|pm).*?\n?', '', text, flags=re.I)
                text = re.sub(r'Read more$', '', text).strip()
                
                if is_bot_response(text):
                    continue
                
                latest_message = text
                break
            except:
                continue
        
        if not latest_message:
            print(f"⏭️ No valid user message found in {chat_display}")
            return
        
        # Create unique message key
        message_key = f"{chat_id}_{latest_message}"
        
        # Check if we already sent a reply to this exact message
        if message_key in processed_messages:
            print(f"⏭️ Already replied to this message in {chat_display}")
            return
        
        # Check if we sent the same message text recently (within 30 seconds)
        if chat_id in last_sent_message:
            last_sent_time, last_sent_text = last_sent_message[chat_id]
            if last_sent_text == latest_message and (now - last_sent_time) < 30:
                print(f"⏭️ Already sent this exact reply to {chat_display} within 30 seconds")
                return
        
        # Check if same as last processed
        if chat_id in last_processed_text and last_processed_text[chat_id] == latest_message:
            print(f"⏭️ Same as last processed message in {chat_display}")
            return
        
        # Check cooldown (15 seconds)
        if chat_id in last_reply_time and now - last_reply_time[chat_id] < 15:
            print(f"⏭️ Cooldown active for {chat_display} (last reply {now - last_reply_time[chat_id]:.0f}s ago)")
            return
        
        print(f"\n📨 Private message from {chat_display}: {latest_message[:100]}")
        
        # Wait for typing to stop
        print("⏳ Waiting for user to finish typing...")
        typing_stopped = wait_for_typing_to_stop(driver, max_wait=12)
        
        if typing_stopped:
            final_delay = random.uniform(0.8, 1.8)
            print(f"⏳ Adding final {final_delay:.1f}s delay...")
            time.sleep(final_delay)
        else:
            print("⚠️ Typing timeout - proceeding with reply")
        
        # Re-check for newer messages (in case something came in while waiting)
        all_messages = driver.find_elements(By.CSS_SELECTOR, "div[class*='message-in'], div[class*='message-out']")
        
        if all_messages:
            last_message = all_messages[-1]
            last_message_class = last_message.get_attribute("class") or ""
            if "message-out" in last_message_class or "outgoing" in last_message_class:
                print(f"📤 Bot already replied while waiting - skipping")
                return
            
            # Get the latest user message again
            current_latest = None
            for msg in reversed(all_messages):
                try:
                    cls = msg.get_attribute("class") or ""
                    if "message-out" in cls or "outgoing" in cls:
                        continue
                    text = msg.text.strip()
                    if text and len(text) > 2 and not is_bot_response(text):
                        text = re.sub(r'\d+:\d+\s*(am|pm).*?\n?', '', text, flags=re.I).strip()
                        if text:
                            current_latest = text
                            break
                except:
                    continue
            
            if current_latest and current_latest != latest_message:
                new_message_key = f"{chat_id}_{current_latest}"
                if new_message_key in processed_messages:
                    print(f"⏭️ Newer message already processed, skipping")
                    return
                print(f"🔄 Newer message arrived, replying to that instead")
                latest_message = current_latest
                message_key = f"{chat_id}_{latest_message}"
        
        # One more check for duplicate before sending
        if message_key in processed_messages:
            print(f"⏭️ Message was processed while waiting, skipping")
            return
        
        # Generate and send reply
        print(f"🤖 Generating reply...")
        reply = router.route(chat_display, latest_message)
        
        if reply:
            if send_reply(driver, reply):
                print(f"✅ Reply sent to {chat_display}")
                processed_messages[message_key] = time.time()
                last_processed_text[chat_id] = latest_message
                last_reply_time[chat_id] = time.time()
                last_sent_message[chat_id] = (time.time(), latest_message)
                
                # 🔥 Record that a bot message was sent (for follow-up tracking)
                InteractionRecorder.record_bot_message(chat_id, chat_display)
            else:
                print(f"❌ Failed to send reply")
        else:
            print("No reply generated")
            
    except Exception as e:
        print(f"Error processing messages: {e}")
    finally:
        # Release lock
        if chat_id in processing_lock:
            del processing_lock[chat_id]


# =========================
# BOT RESPONSE FILTER
# =========================
def is_bot_response(text):
    """Check if text looks like a bot response."""
    patterns = [
        "how can i assist", "happy to help", "services start from", "would you like",
        "let me know", "custom quote", "project details", "web app", "website design",
        "we'd love to help", "bring your vision", "got you covered", "professional website",
        "establish a strong online presence", "looking for information", "have a project",
        "let me know how i can help", "mobile app development", "digital marketing",
        "what type of website", "tell me about your", "starting from", "packages start from"
    ]
    return any(p in text.lower() for p in patterns)


# =========================
# SEND MESSAGE
# =========================
def send_reply(driver, reply_text):
    """Send a reply using clipboard paste."""
    try:
        selectors = [
            "div[contenteditable='true'][data-tab='10']",
            "div[contenteditable='true'][role='textbox']",
            "div[data-testid='conversation-compose-box'] div[contenteditable='true']",
            "footer div[contenteditable='true'][role='textbox']",
        ]

        input_box = None
        for sel in selectors:
            try:
                input_box = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
                )
                if input_box:
                    break
            except:
                continue

        if not input_box:
            return False

        input_box.click()
        time.sleep(0.1)

        # Clear input
        input_box.send_keys(Keys.CONTROL + "a")
        input_box.send_keys(Keys.DELETE)
        time.sleep(0.05)

        # Paste and send
        pyperclip.copy(reply_text)
        input_box.send_keys(Keys.CONTROL + "v")
        time.sleep(0.1)
        input_box.send_keys(Keys.ENTER)

        return True

    except Exception as e:
        print(f"Send failed: {e}")
        return False
"""
WhatsApp Helper - ULTRA-FIXED VERSION with Debugging
This will show EXACTLY what's failing
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class WhatsAppHelper:
    def __init__(self, driver):
        """Initialize with a Selenium WebDriver instance"""
        self.driver = driver
    
    def wait_until_loaded(self, timeout=60):
        """Wait for WhatsApp to load"""
        print("🟡 Waiting for WhatsApp to load...")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#app"))
            )
            time.sleep(2)
            print("✅ WhatsApp loaded successfully")
            return True
        except TimeoutException:
            print("❌ WhatsApp failed to load")
            return False
    
    def open_chat(self, contact_name, timeout=15):
        """
        Open a WhatsApp chat with the specified contact
        """
        try:
            print(f"🔍 Opening chat with {contact_name}...")
            
            # Search box selectors
            search_selectors = [
                '//div[@contenteditable="true"][@data-tab="3"]',
                '//div[@contenteditable="true"][@title="Search input textbox"]',
                'div[contenteditable="true"][data-tab="3"]',
            ]
            
            search = None
            for selector in search_selectors:
                try:
                    if selector.startswith('//'):
                        search = WebDriverWait(self.driver, timeout).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                    else:
                        search = WebDriverWait(self.driver, timeout).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                    if search:
                        break
                except TimeoutException:
                    continue
            
            if not search:
                print("❌ Could not find search box")
                return False
            
            search.click()
            time.sleep(0.5)
            search.clear()
            time.sleep(0.3)
            search.send_keys(contact_name)
            time.sleep(2)
            search.send_keys(Keys.ENTER)
            time.sleep(3)
            
            print(f"✅ Chat opened with {contact_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error opening chat: {e}")
            return False
    
    def send_message(self, message_text):
        """
        Send a message - ULTRA-FIXED with detailed debugging
        """
        print("\n" + "="*60)
        print("📤 SEND MESSAGE DEBUG")
        print("="*60)
        print(f"Message: {message_text[:100]}{'...' if len(message_text) > 100 else ''}")
        
        # Try up to 3 times
        for attempt in range(3):
            try:
                if attempt > 0:
                    print(f"\n🔄 RETRY ATTEMPT {attempt + 1}/3")
                    time.sleep(2)
                
                print(f"\n[Step 1] Finding input box (attempt {attempt + 1})...")
                
                # Your working selectors from the test
                input_selectors = [
                    ("footer div[contenteditable='true']", By.CSS_SELECTOR),
                    ("div[contenteditable='true'][data-tab='10']", By.CSS_SELECTOR),
                    ("footer [contenteditable='true']", By.CSS_SELECTOR),
                ]
                
                input_box = None
                working_selector = None
                
                # Try each selector
                for selector, by_method in input_selectors:
                    print(f"  Trying: {selector}")
                    try:
                        elements = self.driver.find_elements(by_method, selector)
                        print(f"    Found {len(elements)} element(s)")
                        
                        for i, elem in enumerate(elements):
                            try:
                                is_displayed = elem.is_displayed()
                                is_enabled = elem.is_enabled()
                                print(f"    Element {i}: displayed={is_displayed}, enabled={is_enabled}")
                                
                                if is_displayed and is_enabled:
                                    input_box = elem
                                    working_selector = selector
                                    print(f"    ✅ Using element {i}")
                                    break
                            except:
                                print(f"    ⚠️  Element {i} check failed")
                        
                        if input_box:
                            break
                    except Exception as e:
                        print(f"    ❌ Selector failed: {str(e)[:50]}")
                
                # Fallback: Find by footer tag
                if not input_box:
                    print("  Trying footer fallback...")
                    try:
                        footer = self.driver.find_element(By.TAG_NAME, "footer")
                        print(f"    Footer found")
                        contenteditable = footer.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
                        print(f"    Found {len(contenteditable)} contenteditable elements in footer")
                        
                        for i, elem in enumerate(contenteditable):
                            if elem.is_displayed() and elem.is_enabled():
                                input_box = elem
                                working_selector = "footer fallback"
                                print(f"    ✅ Using footer element {i}")
                                break
                    except Exception as e:
                        print(f"    ❌ Footer fallback failed: {str(e)[:50]}")
                
                if not input_box:
                    print("❌ [Step 1] FAILED - No input box found")
                    if attempt < 2:
                        print("   Waiting before retry...")
                        continue
                    else:
                        print("\n" + "="*60)
                        print("❌ SEND FAILED - Could not find input box")
                        print("="*60 + "\n")
                        return False
                
                print(f"✅ [Step 1] SUCCESS - Found via: {working_selector}")
                
                # Step 2: Focus the input
                print("\n[Step 2] Focusing input box...")
                try:
                    # Scroll into view first
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", input_box)
                    time.sleep(0.3)
                    
                    # Click to focus
                    input_box.click()
                    time.sleep(0.5)
                    print("✅ [Step 2] SUCCESS - Input focused")
                except Exception as e:
                    print(f"⚠️  [Step 2] WARNING - Could not click: {str(e)[:50]}")
                    print("   Continuing anyway...")
                
                # Step 3: Clear existing text
                print("\n[Step 3] Clearing existing text...")
                try:
                    input_box.send_keys(Keys.CONTROL + "a")
                    time.sleep(0.1)
                    input_box.send_keys(Keys.BACKSPACE)
                    time.sleep(0.2)
                    print("✅ [Step 3] SUCCESS - Cleared")
                except Exception as e:
                    print(f"⚠️  [Step 3] WARNING - Clear failed: {str(e)[:50]}")
                    print("   Continuing anyway...")
                
                # Step 4: Type message
                print("\n[Step 4] Typing message...")
                try:
                    # Handle multi-line messages
                    lines = message_text.split('\n')
                    for i, line in enumerate(lines):
                        input_box.send_keys(line)
                        if i < len(lines) - 1:
                            # SHIFT+ENTER for new line (don't send yet)
                            input_box.send_keys(Keys.SHIFT + Keys.ENTER)
                    
                    time.sleep(0.7)
                    print(f"✅ [Step 4] SUCCESS - Typed {len(message_text)} chars")
                except Exception as e:
                    print(f"❌ [Step 4] FAILED - {str(e)[:50]}")
                    if attempt < 2:
                        continue
                    else:
                        print("\n" + "="*60)
                        print("❌ SEND FAILED - Could not type message")
                        print("="*60 + "\n")
                        return False
                
                # Step 5: Send message
                print("\n[Step 5] Sending message...")
                try:
                    input_box.send_keys(Keys.ENTER)
                    time.sleep(1.5)
                    print("✅ [Step 5] SUCCESS - Enter pressed")
                except Exception as e:
                    print(f"❌ [Step 5] FAILED - {str(e)[:50]}")
                    if attempt < 2:
                        continue
                    else:
                        print("\n" + "="*60)
                        print("❌ SEND FAILED - Could not press Enter")
                        print("="*60 + "\n")
                        return False
                
                # Step 6: Verify send (optional)
                print("\n[Step 6] Verifying send...")
                try:
                    time.sleep(1)
                    # Check if message appears in chat
                    sent_messages = self.driver.find_elements(By.CSS_SELECTOR, "div.message-out")
                    if sent_messages:
                        last_sent = sent_messages[-1].text[:50]
                        print(f"   Last sent message: {last_sent}...")
                        print("✅ [Step 6] Message appears in chat")
                except Exception as e:
                    print(f"⚠️  [Step 6] Could not verify: {str(e)[:50]}")
                    print("   (Message may still have been sent)")
                
                print("\n" + "="*60)
                print("✅ SEND SUCCESS")
                print("="*60 + "\n")
                return True
                
            except Exception as e:
                print(f"\n❌ ATTEMPT {attempt + 1} EXCEPTION: {e}")
                import traceback
                print("\nFull traceback:")
                traceback.print_exc()
                
                if attempt < 2:
                    print("\nRetrying in 2 seconds...")
                    time.sleep(2)
                else:
                    print("\n" + "="*60)
                    print("❌ SEND FAILED - All attempts exhausted")
                    print("="*60 + "\n")
                    return False
        
        return False
    
    def get_chat_messages(self, last_replied="", count=20):
        """
        Get recent messages from the current chat
        """
        if not last_replied:
            return []
        
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div.message-in, div.message-out")
            elements = elements[-count:][::-1]
            
            messages = []
            for e in elements:
                try:
                    msg_text = e.text.strip()
                    if not msg_text:
                        continue
                    
                    class_name = e.get_attribute("class")
                    if last_replied != msg_text:
                        if "message-in" in class_name:
                            messages.insert(0, msg_text)
                    else:
                        break
                except:
                    continue
            
            return messages
            
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            return []
    
    def get_initial_context(self, context_size=30, my_name="You"):
        """
        Get initial conversation context
        """
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div.message-in, div.message-out")
            elements = elements[-context_size:]
            
            messages = []
            for e in elements:
                try:
                    msg_text = e.text.strip()
                    if not msg_text:
                        continue
                    
                    class_name = e.get_attribute("class")
                    sender = my_name if "message-out" in class_name else "Other"
                    messages.append({"sender": sender, "message": msg_text})
                except:
                    continue
            
            return messages
            
        except Exception as e:
            print(f"❌ Error getting context: {e}")
            return []
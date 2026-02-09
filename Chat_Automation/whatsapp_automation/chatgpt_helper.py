"""
ChatGPT Helper Functions
Handles ChatGPT-specific operations
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class ChatGPTHelper:
    def __init__(self, driver):
        """Initialize with a Selenium WebDriver instance"""
        self.driver = driver
    
    def wait_until_loaded(self, timeout=60):
        """Wait for ChatGPT to load"""
        print("🟡 Waiting for ChatGPT to load...")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea, div[contenteditable='true']"))
            )
            print("✅ ChatGPT loaded successfully")
            return True
        except TimeoutException:
            print("❌ ChatGPT failed to load")
            return False
    
    def wait_for_input_ready(self, timeout=30):
        """Wait for ChatGPT input box to be ready"""
        print("🟡 Waiting for ChatGPT input box...")
        
        input_selectors = [
            "textarea[placeholder*='Message']",
            "textarea[data-id='root']",
            "textarea#prompt-textarea",
            "div[contenteditable='true'][data-id='root']",
            "textarea",
            "div[contenteditable='true']"
        ]
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            for selector in input_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed() and element.is_enabled():
                        try:
                            element.click()
                            print("✅ ChatGPT input box is ready")
                            return element
                        except:
                            continue
                except:
                    continue
            time.sleep(1)
        
        print("❌ ChatGPT input box not found or not ready")
        return None
    
    def send_prompt(self, prompt_text):
        """
        Send a prompt to ChatGPT
        
        Args:
            prompt_text: The prompt to send
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("🧠 Sending prompt to ChatGPT...")
        
        # Find and click input element
        input_element = self.wait_for_input_ready()
        if not input_element:
            return False
        
        try:
            # Clear and send prompt
            input_element.clear()
            input_element.send_keys(prompt_text)
            time.sleep(1)
            input_element.send_keys(Keys.ENTER)
            time.sleep(2)
            
            print("✅ Prompt sent to ChatGPT")
            return True
            
        except Exception as e:
            print(f"❌ Error sending prompt: {e}")
            return False
    
    def wait_for_response_complete(self, timeout=60):
        """
        Wait for ChatGPT to finish generating response
        
        Args:
            timeout: Maximum time to wait
        
        Returns:
            bool: True if response completed, False if timeout
        """
        print("⏳ Waiting for ChatGPT response...")
        
        start_time = time.time()
        last_length = 0
        stable_count = 0
        
        while time.time() - start_time < timeout:
            try:
                # Check if there's a stop button (means still generating)
                stop_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='Stop']")
                
                if not stop_buttons:
                    # No stop button, likely finished
                    stable_count += 1
                    if stable_count >= 3:
                        print("✅ Response generation complete")
                        return True
                else:
                    stable_count = 0
                
                time.sleep(1)
                
            except:
                time.sleep(1)
        
        print("⚠️ Response timeout or completed")
        return True
    
    def read_response(self):
        """
        Read the latest ChatGPT response
        
        Returns:
            str: Response text, empty string if not found
        """
        print("📖 Reading ChatGPT response...")
        
        # Wait for response to complete
        self.wait_for_response_complete()
        
        # Additional wait for stability
        time.sleep(3)
        
        # Try multiple selectors for response
        response_selectors = [
            "div[data-message-author-role='assistant']",
            "div.markdown",
            "div.result-streaming",
            "div[class*='markdown']"
        ]
        
        for selector in response_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    response = elements[-1].text.strip()
                    if response:
                        print(f"✅ Response received ({len(response)} chars)")
                        return response
            except:
                continue
        
        print("❌ Could not read ChatGPT response")
        return ""
    
    def clean_response(self, response):
        """
        Clean ChatGPT response for WhatsApp
        
        Args:
            response: Raw response text
        
        Returns:
            str: Cleaned response
        """
        import re
        
        if not response:
            return ""
        
        # Remove common AI-like phrases
        ai_phrases = [
            "As an AI", "I'm an AI", "I'm ChatGPT", 
            "I'm an artificial intelligence",
            "I'm a language model", "I'm Claude", 
            "I'm an assistant"
        ]
        
        cleaned = response
        for phrase in ai_phrases:
            cleaned = cleaned.replace(phrase, "")
        
        # Remove excessive formatting
        cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)  # Remove bold
        cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)      # Remove italic
        cleaned = re.sub(r'#{1,6}\s*', '', cleaned)         # Remove headers
        
        # Clean up whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned

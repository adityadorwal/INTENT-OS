"""
Chrome Driver Manager
Handles Chrome profile loading and driver initialization
"""

import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class ChromeManager:
    def __init__(self, config_file=None):
        """Initialize Chrome Manager with config file"""
        if config_file is None:
            # Find chrome_profile.json in main project directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Try different possible locations
            possible_paths = [
                os.path.join(current_dir, '..', '..', 'chrome_profile.json'),  # from whatsapp_automation
                os.path.join(current_dir, '..', 'chrome_profile.json'),        # from Chat_Automation
                os.path.join(current_dir, 'chrome_profile.json'),               # from main project
            ]
            
            config_file = None
            for path in possible_paths:
                if os.path.exists(path):
                    config_file = path
                    break
            
            if not config_file:
                raise FileNotFoundError(
                    f"chrome_profile.json not found in any expected location. "
                    f"Please create it in the main project directory."
                )
        
        if not os.path.exists(config_file):
            raise FileNotFoundError(
                f"Chrome profile config not found. Please create '{config_file}' "
                "in the main directory with your Chrome profile paths."
            )
        
        with open(config_file, 'r') as f:
            chrome_config = json.load(f)
            # Extract chrome profile config
            self.config = chrome_config.get('chrome_profiles', {})
            
            if not self.config:
                raise ValueError(
                    "Chrome profiles not found in chrome_profile.json. "
                    "Please add 'chrome_profiles' section with whatsapp_profile and chatgpt_profile."
                )
    
    def get_whatsapp_profile(self):
        """Get WhatsApp Chrome profile path"""
        return self.config.get('whatsapp_profile', '')
    
    def get_chatgpt_profile(self):
        """Get ChatGPT Chrome profile path"""
        return self.config.get('chatgpt_profile', '')
    
    def get_whatsapp_url(self):
        """Get WhatsApp URL"""
        return self.config.get('whatsapp_url', 'https://web.whatsapp.com/')
    
    def launch_driver(self, profile_type='whatsapp'):
        """
        Launch Chrome driver with specified profile
        
        Args:
            profile_type: 'whatsapp' or 'chatgpt'
        
        Returns:
            WebDriver instance
        """
        if profile_type == 'whatsapp':
            profile_path = self.get_whatsapp_profile()
        elif profile_type == 'chatgpt':
            profile_path = self.get_chatgpt_profile()
        else:
            raise ValueError(f"Invalid profile_type: {profile_type}")
        
        if not profile_path:
            raise ValueError(f"Profile path for {profile_type} not configured")
        
        opts = Options()
        opts.add_argument(f"--user-data-dir={profile_path}")
        opts.add_argument("--profile-directory=Default")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        opts.add_argument("--log-level=3")
        opts.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = webdriver.Chrome(options=opts)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def close_driver(self, driver):
        """Safely close a driver instance"""
        try:
            if driver:
                driver.quit()
                return True
        except Exception as e:
            print(f"Error closing driver: {e}")
            return False

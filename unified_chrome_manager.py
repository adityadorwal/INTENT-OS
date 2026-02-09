"""
Unified Chrome Manager
Central Chrome management for all automations (WhatsApp, Forms, Web, etc.)

This solves the Chrome profile conflicts by:
1. Using a single Chrome profile for all automations
2. Managing debugging port properly
3. Tab-based approach instead of multiple Chrome instances
4. Session persistence across automations

Usage:
    from unified_chrome_manager import UnifiedChromeManager
    
    chrome = UnifiedChromeManager()
    driver = chrome.get_driver()  # Gets or creates driver
    # ... use driver ...
    chrome.close()  # Closes when done
"""

import os
import json
import time
import psutil
import subprocess
from pathlib import Path
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


class UnifiedChromeManager:
    """
    Unified Chrome Manager - Single source of truth for Chrome automation
    
    Features:
    - Single Chrome profile for all automations
    - Automatic debugging port management
    - Tab-based multi-tasking
    - Session persistence
    - Proper cleanup
    """
    
    # Singleton instance
    _instance = None
    _driver = None
    
    def __new__(cls):
        """Singleton pattern - only one instance exists"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Chrome manager"""
        if not hasattr(self, 'initialized'):
            self.config = self._load_config()
            self.profile_path = self.config.get('unified_profile_path', '')
            self.debug_port = self.config.get('debug_port', 9222)
            self.initialized = True
            print(f"🌐 Unified Chrome Manager initialized")
            print(f"   Profile: {self.profile_path}")
            print(f"   Debug Port: {self.debug_port}")
    
    def _load_config(self) -> dict:
        """Load configuration from chrome_profile.json"""
        try:
            # Find config file
            project_root = Path(__file__).parent
            config_path = project_root / "chrome_profile.json"
            
            if not config_path.exists():
                print("⚠️  chrome_profile.json not found, using defaults")
                return self._create_default_config()
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check if unified config exists
            if 'unified_chrome' not in config:
                print("⚠️  Unified Chrome config missing, updating...")
                return self._update_config(config)
            
            return config['unified_chrome']
            
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> dict:
        """Create default configuration"""
        import platform
        
        if platform.system() == 'Windows':
            default_profile = os.path.expandvars(
                r"%LOCALAPPDATA%\Google\Chrome\User Data\AutomationProfile"
            )
        elif platform.system() == 'Darwin':  # macOS
            default_profile = os.path.expanduser(
                "~/Library/Application Support/Google/Chrome/AutomationProfile"
            )
        else:  # Linux
            default_profile = os.path.expanduser(
                "~/.config/google-chrome/AutomationProfile"
            )
        
        return {
            'unified_profile_path': default_profile,
            'debug_port': 9222,
            'headless': False,
            'window_size': '1920,1080'
        }
    
    def _update_config(self, existing_config: dict) -> dict:
        """Update existing config with unified Chrome settings"""
        # Use the first available profile as unified profile
        profiles = existing_config.get('chrome_profiles', {})
        
        unified_profile = (
            profiles.get('whatsapp_profile', '') or
            profiles.get('chatgpt_profile', '') or
            existing_config.get('form_filler', {}).get('profile_path', '')
        )
        
        unified_config = {
            'unified_profile_path': unified_profile,
            'debug_port': 9222,
            'headless': False,
            'window_size': '1920,1080'
        }
        
        # Save updated config
        existing_config['unified_chrome'] = unified_config
        
        config_path = Path(__file__).parent / "chrome_profile.json"
        try:
            with open(config_path, 'w') as f:
                json.dump(existing_config, f, indent=4)
            print("✅ Updated chrome_profile.json with unified settings")
        except Exception as e:
            print(f"⚠️  Could not save config: {e}")
        
        return unified_config
    
    def is_chrome_running(self) -> bool:
        """Check if Chrome is already running with our debugging port"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline:
                        cmdline_str = ' '.join(cmdline)
                        if f'remote-debugging-port={self.debug_port}' in cmdline_str:
                            return True
            return False
        except Exception as e:
            print(f"⚠️  Error checking Chrome: {e}")
            return False
    
    def start_chrome_process(self) -> bool:
        """Start Chrome with remote debugging enabled"""
        try:
            if self.is_chrome_running():
                print("ℹ️  Chrome already running with debugging")
                return True
            
            print(f"🚀 Starting Chrome with debugging...")
            
            # Find Chrome executable
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
            ]
            
            chrome_exe = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_exe = path
                    break
            
            if not chrome_exe:
                raise FileNotFoundError("Chrome executable not found!")
            
            # Build command
            cmd = [
                chrome_exe,
                f"--remote-debugging-port={self.debug_port}",
                f"--user-data-dir={self.profile_path}",
                "--no-first-run",
                "--no-default-browser-check",
            ]
            
            # Start Chrome in background
            if os.name == 'nt':  # Windows
                subprocess.Popen(
                    cmd,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:  # Linux/Mac
                subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            
            print("✅ Chrome started")
            time.sleep(3)  # Wait for Chrome to initialize
            return True
            
        except Exception as e:
            print(f"❌ Error starting Chrome: {e}")
            return False
    
    def get_driver(self, new_tab: bool = False) -> webdriver.Chrome:
        """
        Get Chrome driver instance
        
        Args:
            new_tab: If True, opens a new tab. If False, reuses existing driver.
        
        Returns:
            WebDriver instance
        """
        # If we already have a driver and don't need new tab, return it
        if self._driver and not new_tab:
            return self._driver
        
        # Start Chrome if not running
        if not self.is_chrome_running():
            self.start_chrome_process()
        
        # Connect to Chrome via debugging
        try:
            chrome_options = Options()
            chrome_options.add_experimental_option(
                "debuggerAddress", 
                f"127.0.0.1:{self.debug_port}"
            )
            
            driver = webdriver.Chrome(options=chrome_options)
            
            if new_tab:
                # Open new tab
                driver.execute_script("window.open('about:blank', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])
            else:
                # Store as main driver
                self._driver = driver
            
            return driver
            
        except Exception as e:
            print(f"❌ Error connecting to Chrome: {e}")
            print(f"💡 Make sure Chrome is running on port {self.debug_port}")
            raise
    
    def open_url(self, url: str, new_tab: bool = True) -> webdriver.Chrome:
        """
        Open URL in Chrome
        
        Args:
            url: URL to open
            new_tab: Open in new tab (default) or current tab
        
        Returns:
            WebDriver instance
        """
        driver = self.get_driver(new_tab=new_tab)
        driver.get(url)
        return driver
    
    def open_whatsapp(self, new_tab: bool = True) -> webdriver.Chrome:
        """Open WhatsApp Web in Chrome"""
        print("📱 Opening WhatsApp Web...")
        return self.open_url("https://web.whatsapp.com/", new_tab=new_tab)
    
    def open_chatgpt(self, new_tab: bool = True) -> webdriver.Chrome:
        """Open ChatGPT in Chrome"""
        print("🤖 Opening ChatGPT...")
        return self.open_url("https://chat.openai.com/", new_tab=new_tab)
    
    def close_tab(self, driver: Optional[webdriver.Chrome] = None):
        """Close current tab (but keep Chrome running)"""
        try:
            if driver:
                driver.close()
            elif self._driver:
                # Don't close main driver, just close the tab
                if len(self._driver.window_handles) > 1:
                    self._driver.close()
        except Exception as e:
            print(f"⚠️  Error closing tab: {e}")
    
    def close(self, keep_chrome_running: bool = True):
        """
        Close driver
        
        Args:
            keep_chrome_running: If True, keeps Chrome open (default)
                                If False, quits Chrome completely
        """
        try:
            if self._driver:
                if keep_chrome_running:
                    # Just close the current tab
                    self.close_tab(self._driver)
                else:
                    # Quit completely
                    self._driver.quit()
                    self._driver = None
                    print("✅ Chrome closed")
        except Exception as e:
            print(f"⚠️  Error during cleanup: {e}")
    
    def cleanup(self):
        """Full cleanup - close everything"""
        self.close(keep_chrome_running=False)
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.cleanup()
        except:
            pass


# Convenience functions for backward compatibility
def get_chrome_driver(new_tab: bool = False) -> webdriver.Chrome:
    """Get Chrome driver (convenience function)"""
    manager = UnifiedChromeManager()
    return manager.get_driver(new_tab=new_tab)


def open_whatsapp() -> webdriver.Chrome:
    """Open WhatsApp Web (convenience function)"""
    manager = UnifiedChromeManager()
    return manager.open_whatsapp()


def close_chrome():
    """Close Chrome (convenience function)"""
    manager = UnifiedChromeManager()
    manager.close()


# Test function
def test_unified_chrome():
    """Test the unified Chrome manager"""
    print("\n" + "="*60)
    print("🧪 Testing Unified Chrome Manager")
    print("="*60)
    
    manager = UnifiedChromeManager()
    
    print("\n1️⃣ Testing Chrome startup...")
    driver = manager.get_driver()
    print("✅ Chrome connected!")
    
    print("\n2️⃣ Testing URL opening...")
    driver.get("https://www.google.com")
    print("✅ Opened Google")
    time.sleep(2)
    
    print("\n3️⃣ Testing new tab...")
    driver2 = manager.get_driver(new_tab=True)
    driver2.get("https://www.youtube.com")
    print("✅ Opened YouTube in new tab")
    time.sleep(2)
    
    print("\n4️⃣ Testing WhatsApp shortcut...")
    wa_driver = manager.open_whatsapp(new_tab=True)
    print("✅ Opened WhatsApp Web")
    time.sleep(2)
    
    print("\n5️⃣ Testing cleanup...")
    manager.close_tab(wa_driver)
    print("✅ Closed WhatsApp tab")
    time.sleep(1)
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("💡 Chrome is still running in the background")
    print("="*60)


if __name__ == "__main__":
    test_unified_chrome()

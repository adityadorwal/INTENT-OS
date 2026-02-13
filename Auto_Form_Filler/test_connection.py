"""
Test Chrome Connection
Quick script to test if Chrome debugging connection works
"""

import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_chrome_connection():
    """Test Chrome connection"""
    print("\n" + "="*60)
    print("🧪 CHROME CONNECTION TEST")
    print("="*60)
    
    # Load config
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chrome_profile.json")
        print(f"\n📁 Loading config from: {config_path}")
        
        if not os.path.exists(config_path):
            print("❌ chrome_profile.json not found!")
            print(f"Expected location: {config_path}")
            input("\nPress Enter to close...")
            return
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        form_filler_config = config.get('form_filler', {})
        debug_port = form_filler_config.get('debug_port', 9222)
        profile_path = form_filler_config.get('profile_path', '')
        
        print(f"✅ Config loaded")
        print(f"   Debug Port: {debug_port}")
        print(f"   Profile Path: {profile_path}")
        
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        input("\nPress Enter to close...")
        return
    
    # Test connection
    print(f"\n🔌 Attempting to connect to Chrome on port {debug_port}...")
    
    try:
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        print("✅ Connection successful!")
        print(f"   Current URL: {driver.current_url}")
        print(f"   Window Title: {driver.title}")
        
        # Don't close the driver
        print("\n" + "="*60)
        print("✅ TEST PASSED - Chrome connection works!")
        print("="*60)
        print("\n💡 You can now use the auto form filler")
        
    except Exception as e:
        print(f"\n❌ Connection failed!")
        print(f"Error: {e}")
        print("\n" + "="*60)
        print("TROUBLESHOOTING:")
        print("1. Make sure Chrome is running")
        print("2. Chrome must be started with debugging enabled:")
        print(f'   chrome.exe --remote-debugging-port={debug_port} --user-data-dir="{profile_path}"')
        print("3. Check if another program is using the port")
        print("4. Try closing all Chrome windows and restart")
        print("="*60)
    
    input("\nPress Enter to close...")

if __name__ == "__main__":
    test_chrome_connection()

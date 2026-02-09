"""
Manual Send Message Script
Send a single message to a WhatsApp contact and close the browser

Usage:
    python send_message.py
    
    OR from Python:
    from send_message import send_whatsapp_message
    send_whatsapp_message("Contact Name", "Your message here")
"""

import time
from chrome_manager import ChromeManager
from whatsapp_helper import WhatsAppHelper

def send_whatsapp_message(contact_name, message_text, wait_after_send=2):
    """
    Send a message to a WhatsApp contact and close the browser
    
    Args:
        contact_name (str): Name of the WhatsApp contact
        message_text (str): Message to send
        wait_after_send (int): Seconds to wait after sending before closing
    
    Returns:
        bool: True if successful, False otherwise
    """
    driver = None
    
    try:
        print("=" * 60)
        print("🚀 WhatsApp Message Sender")
        print("=" * 60)
        
        # Initialize Chrome manager
        chrome_manager = ChromeManager()
        
        # Launch WhatsApp
        print("\n📱 Launching WhatsApp...")
        driver = chrome_manager.launch_driver('whatsapp')
        driver.get(chrome_manager.get_whatsapp_url())
        
        # Create WhatsApp helper
        wa_helper = WhatsAppHelper(driver)
        
        # Wait for WhatsApp to load
        if not wa_helper.wait_until_loaded():
            print("❌ Failed to load WhatsApp")
            return False
        
        # Open the chat
        if not wa_helper.open_chat(contact_name):
            print(f"❌ Failed to open chat with {contact_name}")
            return False
        
        # Send the message
        if not wa_helper.send_message(message_text):
            print("❌ Failed to send message")
            return False
        
        print(f"\n✅ Message sent successfully to {contact_name}!")
        print(f"📝 Message: {message_text[:50]}{'...' if len(message_text) > 50 else ''}")
        
        # Wait a bit before closing
        print(f"\n⏳ Waiting {wait_after_send} seconds before closing...")
        time.sleep(wait_after_send)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Always close the browser
        if driver:
            print("\n🧹 Closing browser...")
            chrome_manager.close_driver(driver)
            print("✅ Browser closed")
        print("=" * 60)

def main():
    """Interactive mode for sending messages"""
    print("\n" + "=" * 60)
    print("📱 WhatsApp Manual Message Sender")
    print("=" * 60)
    
    contact_name = input("\n👤 Enter contact name: ").strip()
    if not contact_name:
        print("❌ Contact name cannot be empty!")
        return
    
    print("\n💬 Enter your message (press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if line:
            lines.append(line)
        else:
            if lines:
                break
            else:
                print("Type your message:")
    
    message_text = '\n'.join(lines)
    
    if not message_text:
        print("❌ Message cannot be empty!")
        return
    
    # Confirm
    print("\n" + "-" * 60)
    print(f"📤 Ready to send:")
    print(f"   To: {contact_name}")
    print(f"   Message: {message_text[:100]}{'...' if len(message_text) > 100 else ''}")
    print("-" * 60)
    
    confirm = input("\n✅ Send this message? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        send_whatsapp_message(contact_name, message_text)
    else:
        print("❌ Message sending cancelled")

if __name__ == "__main__":
    main()

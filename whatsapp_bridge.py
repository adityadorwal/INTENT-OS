"""
WhatsApp Bridge - Integration between Intent_OS and WhatsApp Automation
IMPROVED VERSION with retry logic and better error handling

This module provides a simple interface for Intent_OS to send WhatsApp messages
via voice commands without dealing with the complexity of the automation system.

Usage from Intent_OS:
    from whatsapp_bridge import send_whatsapp_message
    success = send_whatsapp_message("John", "Hello!")
"""

import sys
import os
import time
from pathlib import Path
from typing import Optional

# Import logging
from logger_config import get_logger

logger = get_logger("whatsapp_bridge")

# Add Chat_Automation to path
chat_automation_path = Path(__file__).parent / "Chat_Automation" / "whatsapp_automation"
sys.path.insert(0, str(chat_automation_path))


def send_whatsapp_message(
    recipient: str, 
    message: str, 
    wait_after_send: int = 4,
    max_retries: int = 3,
    retry_delay: int = 5
) -> bool:
    """
    Send a WhatsApp message via voice command with retry logic
    
    Args:
        recipient: Contact name in WhatsApp
        message: Message text to send
        wait_after_send: Seconds to wait before closing (default: 2)
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Seconds to wait between retries (default: 5)
    
    Returns:
        bool: True if message sent successfully, False otherwise
    
    Example:
        success = send_whatsapp_message("John", "Hello from voice assistant!")
    """
    attempt = 0
    last_error = None
    
    while attempt < max_retries:
        attempt += 1
        
        try:
            logger.info(f"Attempt {attempt}/{max_retries}: Sending WhatsApp message to {recipient}")
            print(f"\n📱 [WhatsApp Bridge] Attempt {attempt}/{max_retries}")
            print(f"📤 Sending to: {recipient}")
            print(f"💬 Message: {message[:50]}{'...' if len(message) > 50 else ''}")
            
            # Import the WhatsApp sender (only import when needed)
            from send_message import send_whatsapp_message as whatsapp_send
            
            # Send the message
            success = whatsapp_send(recipient, message, wait_after_send)
            
            if success:
                logger.info(f"Message sent successfully on attempt {attempt}")
                print(f"✅ [WhatsApp Bridge] Message sent successfully!")
                return True
            else:
                logger.warning(f"Message send returned False on attempt {attempt}")
                raise Exception("WhatsApp send returned False")
            
        except ImportError as e:
            logger.error(f"Import error: {e}", exc_info=True)
            print(f"❌ [WhatsApp Bridge] Import error: {e}")
            print(f"💡 Make sure Chat_Automation folder exists with all required files")
            return False  # Don't retry on import errors
        
        except Exception as e:
            last_error = e
            logger.warning(f"Attempt {attempt} failed: {e}")
            print(f"⚠️  [WhatsApp Bridge] Attempt {attempt} failed: {e}")
            
            # If not the last attempt, wait and retry
            if attempt < max_retries:
                print(f"🔄 Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                # Last attempt failed
                logger.error(f"All {max_retries} attempts failed. Last error: {last_error}", exc_info=True)
                print(f"❌ [WhatsApp Bridge] All {max_retries} attempts failed")
                print(f"❌ Last error: {last_error}")
                import traceback
                traceback.print_exc()
                return False
    
    return False


def is_whatsapp_available() -> bool:
    """
    Check if WhatsApp automation is available
    
    Returns:
        bool: True if all required files exist
    """
    try:
        required_files = [
            "Chat_Automation/whatsapp_automation/send_message.py",
            "Chat_Automation/whatsapp_automation/whatsapp_helper.py",
            "Chat_Automation/whatsapp_automation/chrome_manager.py",
        ]
        
        for file_path in required_files:
            full_path = Path(__file__).parent / file_path
            if not full_path.exists():
                logger.warning(f"Missing required file: {file_path}")
                print(f"⚠️  Missing: {file_path}")
                return False
        
        logger.info("All WhatsApp automation files present")
        return True
        
    except Exception as e:
        logger.error(f"Error checking WhatsApp availability: {e}")
        print(f"❌ Error checking WhatsApp availability: {e}")
        return False


# Test function
def test_whatsapp_bridge():
    """Test the WhatsApp bridge (for debugging)"""
    print("\n" + "=" * 60)
    print("🧪 Testing WhatsApp Bridge")
    print("=" * 60)
    
    # Check availability
    print("\n1️⃣ Checking WhatsApp availability...")
    available = is_whatsapp_available()
    
    if available:
        print("✅ WhatsApp automation is available!")
    else:
        print("❌ WhatsApp automation is NOT available")
        print("💡 Make sure Chat_Automation folder is properly set up")
        return
    
    # Ask for test message
    print("\n2️⃣ Test sending a message (optional)")
    choice = input("Do you want to send a test message? (yes/no): ").strip().lower()
    
    if choice in ['yes', 'y']:
        recipient = input("Enter recipient name: ").strip()
        message = input("Enter message: ").strip()
        
        if recipient and message:
            print(f"\n3️⃣ Sending test message...")
            success = send_whatsapp_message(recipient, message)
            
            if success:
                print("\n✅ Test successful!")
            else:
                print("\n❌ Test failed!")
        else:
            print("❌ Recipient and message cannot be empty!")
    else:
        print("⏭️  Skipping test message")
    
    print("\n" + "=" * 60)
    print("✅ WhatsApp Bridge test complete!")
    print("=" * 60)


if __name__ == "__main__":
    # Run test when executed directly
    test_whatsapp_bridge()
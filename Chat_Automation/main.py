"""
WhatsApp Automation Launcher
Main entry point for the automation system
"""

import sys
import os

def print_menu():
    """Display main menu"""
    print("\n" + "=" * 60)
    print("🤖 WhatsApp Automation System")
    print("=" * 60)
    print("\nChoose a mode:\n")
    print("1. 🔄 Automated Chatbot (Full automation with AI)")
    print("2. 📤 Send Manual Message (Send once and close)")
    print("3. ❌ Exit")
    print("\n" + "=" * 60)

def launch_automated_chatbot():
    """Launch the automated chatbot GUI"""
    print("\n🚀 Launching Automated Chatbot...\n")
    script_dir = os.path.join(os.path.dirname(__file__), 'whatsapp_automation')
    os.chdir(script_dir)
    os.system(f'{sys.executable} automated_chatbot.py')

def launch_manual_sender():
    """Launch the manual message sender"""
    print("\n📤 Launching Manual Message Sender...\n")
    script_dir = os.path.join(os.path.dirname(__file__), 'whatsapp_automation')
    os.chdir(script_dir)
    os.system(f'{sys.executable} send_message.py')

def main():
    """Main launcher"""
    while True:
        print_menu()
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            launch_automated_chatbot()
        elif choice == '2':
            launch_manual_sender()
        elif choice == '3':
            print("\n👋 Goodbye!\n")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1, 2, or 3.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!\n")
        sys.exit(0)

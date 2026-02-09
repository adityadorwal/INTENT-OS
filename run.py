#!/usr/bin/env python3
"""
Simple run script that checks if setup is complete
and launches the main application
"""

import sys
import os
from pathlib import Path
import subprocess

def check_setup_complete():
    """Check if first-time setup has been completed"""
    flag_file = Path('.setup_complete')
    return flag_file.exists()

def check_env_file():
    """Check if .env file exists"""
    env_file = Path('.env')
    return env_file.exists()

def main():
    print("=" * 60)
    print("Voice Command AI - Launcher".center(60))
    print("=" * 60)
    print()
    
    # Check if setup is complete
    if not check_setup_complete() or not check_env_file():
        print("⚠️  First-time setup required!")
        print()
        print("It looks like this is your first time running the application.")
        print("Please run the setup wizard first:")
        print()
        print("  python setup.py")
        print()
        print("The setup wizard will guide you through:")
        print("  • API key configuration")
        print("  • Chrome profile setup")
        print("  • Personal data for form filling")
        print()
        sys.exit(1)
    
    # Setup is complete, launch main application
    print("✓ Setup complete! Launching application...")
    print()
    
    try:
        subprocess.run([sys.executable, 'main.py'], check=True)
    except KeyboardInterrupt:
        print("\n\nApplication stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error launching application: {e}")
        print("\nCheck logs/ directory for error details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
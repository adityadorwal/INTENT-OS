"""
Quick fix for TTS (Text-to-Speech)
Install pyttsx3 for voice responses
"""

import subprocess
import sys

def install_tts():
    """Install pyttsx3 for TTS"""
    print("🔊 Installing Text-to-Speech support...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'pyttsx3'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ pyttsx3 installed successfully!")
            print("\n🎉 TTS is now available!")
            print("Intent OS will now speak responses back to you.")
        else:
            print(f"❌ Installation failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to close...")

if __name__ == "__main__":
    install_tts()
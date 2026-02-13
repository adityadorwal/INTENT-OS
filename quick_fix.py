"""
Quick Fix - Install missing dependencies
Agar GUI setup nahi use karna chahte toh yeh run karo
"""

import subprocess
import sys

def install_missing_packages():
    """Install all missing packages"""
    packages = [
        'python-dotenv',
        'PyQt5',
        'selenium', 
        'SpeechRecognition',
        'PyAudio',
        'psutil',
        'requests',
        'pyttsx3'
    ]
    
    print("🚀 Installing missing packages...")
    print("=" * 50)
    
    for package in packages:
        print(f"\nInstalling {package}...")
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', package],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {package} installed")
            else:
                print(f"❌ {package} failed: {result.stderr}")
        except Exception as e:
            print(f"❌ {package} error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Installation complete!")
    print("\nNow run: python run.py")
    input("\nPress Enter to close...")

if __name__ == "__main__":
    install_missing_packages()
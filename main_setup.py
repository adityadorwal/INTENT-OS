import subprocess
import json
import os
import time
import psutil
from pathlib import Path

def find_chrome_executable():
    """Find Chrome executable across different Windows installations"""
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def get_chrome_user_data_dir():
    """Get the default Chrome user data directory"""
    return os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")

def get_chrome_profiles(user_data_dir):
    """Get list of existing Chrome profiles"""
    profiles = []
    
    if not os.path.exists(user_data_dir):
        return profiles
    
    # Check for Default profile
    default_profile = os.path.join(user_data_dir, "Default")
    if os.path.exists(default_profile):
        profiles.append({"name": "Default", "path": default_profile})
    
    # Check for numbered profiles (Profile 1, Profile 2, etc.)
    for item in os.listdir(user_data_dir):
        item_path = os.path.join(user_data_dir, item)
        if os.path.isdir(item_path) and item.startswith("Profile "):
            profiles.append({"name": item, "path": item_path})
    
    return profiles

def save_profile_to_json(profile_path, filename="chrome_profile.json"):
    """
    Save the selected profile path to a JSON file in the CORRECT format
    that all components expect (form_filler, whatsapp, unified_chrome)
    
    FIXED: Now creates proper structure with all required sections
    """
    
    # Check if file already exists and load it
    existing_data = {}
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                existing_data = json.load(f)
            print(f"ℹ️  Updating existing {filename}")
        except Exception as e:
            print(f"⚠️  Could not read existing {filename}, creating new one")
            print(f"    Reason: {e}")
    
    # Create/update the complete structure
    # This structure is required by:
    # - form_filler_launcher.py (needs form_filler section)
    # - unified_chrome_manager.py (needs unified_chrome section)
    # - whatsapp_bridge.py (needs chrome_profiles section)
    data = {
        "chrome_profiles": {
            "whatsapp_profile": profile_path,  # Use same profile for all automations
            "chatgpt_profile": profile_path,
            "whatsapp_url": "https://web.whatsapp.com/"
        },
        "form_filler": {
            "profile_path": profile_path,
            "debug_port": 9222
        },
        "unified_chrome": {
            "unified_profile_path": profile_path,
            "debug_port": 9222,
            "headless": False,
            "window_size": "1920,1080"
        },
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Merge with existing data (preserve any custom settings)
    if existing_data:
        # Update each section while preserving other settings
        for key in ["chrome_profiles", "form_filler", "unified_chrome"]:
            if key in existing_data and isinstance(existing_data[key], dict):
                # Merge: update existing values, keep others
                existing_data[key].update(data[key])
            else:
                # Create new section
                existing_data[key] = data[key]
        existing_data["timestamp"] = data["timestamp"]
        data = existing_data
    
    # Save to file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"\n✅ Profile configuration saved to {filename}")
    print(f"   Profile: {profile_path}")
    print(f"   Debug Port: 9222")
    print(f"\n📋 Configuration includes:")
    print(f"   • WhatsApp automation profile")
    print(f"   • Form filler configuration")
    print(f"   • Unified Chrome manager settings")

def validate_chrome_config(filename="chrome_profile.json"):
    """
    Validate that chrome_profile.json has the correct structure
    required by all components
    
    NEW: Added to catch configuration errors early
    """
    try:
        if not os.path.exists(filename):
            print(f"❌ {filename} not found")
            return False
        
        with open(filename, 'r') as f:
            config = json.load(f)
        
        # Check required sections
        required_sections = {
            "chrome_profiles": ["whatsapp_profile"],
            "form_filler": ["profile_path", "debug_port"],
            "unified_chrome": ["unified_profile_path", "debug_port"]
        }
        
        all_valid = True
        
        for section, fields in required_sections.items():
            if section not in config:
                print(f"❌ Missing section: '{section}'")
                all_valid = False
                continue
            
            for field in fields:
                if field not in config[section]:
                    print(f"❌ Missing field '{field}' in section '{section}'")
                    all_valid = False
        
        if all_valid:
            print(f"✅ {filename} structure is valid")
            print(f"   All required sections present:")
            print(f"   • chrome_profiles ✓")
            print(f"   • form_filler ✓")
            print(f"   • unified_chrome ✓")
        
        return all_valid
        
    except json.JSONDecodeError:
        print(f"❌ {filename} is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Error validating {filename}: {e}")
        return False

def open_chrome_profile_selector():
    """Open Chrome with profile selector"""
    chrome_path = find_chrome_executable()
    
    if not chrome_path:
        print("❌ Error: Chrome executable not found!")
        print("Please install Google Chrome or provide the correct path.")
        return None
    
    print(f"✅ Found Chrome at: {chrome_path}")
    
    user_data_dir = get_chrome_user_data_dir()
    print(f"✅ Chrome User Data Directory: {user_data_dir}")
    
    # Get existing profiles
    profiles = get_chrome_profiles(user_data_dir)
    
    if profiles:
        print(f"\n📋 Found {len(profiles)} existing profile(s):")
        for idx, profile in enumerate(profiles, 1):
            print(f"  {idx}. {profile['name']}")
    else:
        print("\nℹ️  No existing profiles found.")
    
    print("\n" + "=" * 60)
    print("Opening Chrome Profile Selector...")
    print("=" * 60)
    print("📌 Please select a profile or create a new one in Chrome.")
    print("📌 After selecting/creating a profile, return here and press Enter.")
    print()
    
    # Open Chrome with profile picker
    # The --profile-directory flag with an empty value shows the profile picker
    try:
        subprocess.Popen([chrome_path, "--profile-directory="])
        print("✅ Chrome opened successfully!")
    except Exception as e:
        print(f"❌ Error opening Chrome: {e}")
        return None
    
    # Wait for user to select profile
    input("\n⏸️  Press Enter after you've selected or created a profile in Chrome...")
    
    return user_data_dir

def detect_active_chrome_profile(user_data_dir):
    """Detect which Chrome profile is currently active"""
    try:
        print("🔍 Detecting active Chrome profile...")
        
        # Look for Chrome processes and their command line arguments
        for proc in psutil.process_iter(['name', 'cmdline']):
            if proc.info['name'] and 'chrome.exe' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline:
                    for arg in cmdline:
                        if '--profile-directory=' in arg:
                            profile_name = arg.split('--profile-directory=')[1]
                            profile_path = os.path.join(user_data_dir, profile_name)
                            print(f"✅ Detected active profile: {profile_name}")
                            return profile_path
        
        # If no specific profile found, assume Default
        default_profile = os.path.join(user_data_dir, "Default")
        if os.path.exists(default_profile):
            print(f"ℹ️  Using default profile")
            return default_profile
            
    except Exception as e:
        print(f"⚠️  Error detecting active profile: {e}")
    
    return None

def main():
    print("=" * 60)
    print("      CHROME PROFILE SETUP - INTENT-OS")
    print("=" * 60)
    print()
    print("This setup will configure Chrome for:")
    print("  • WhatsApp automation")
    print("  • Auto Form Filler")
    print("  • Unified Chrome manager")
    print()
    print("=" * 60)
    print()
    
    user_data_dir = open_chrome_profile_selector()
    
    if not user_data_dir:
        print("\n❌ Setup failed: Could not access Chrome")
        return
    
    print("\n" + "=" * 60)
    print("Detecting selected profile...")
    print("=" * 60)
    time.sleep(2)  # Give Chrome time to start
    
    profile_path = detect_active_chrome_profile(user_data_dir)
    
    if profile_path:
        save_profile_to_json(profile_path)
    else:
        print("\n⚠️  Couldn't automatically detect the profile.")
        print("Listing available profiles:")
        
        profiles = get_chrome_profiles(user_data_dir)
        
        if not profiles:
            print("\nℹ️  No profiles found. Using default profile path.")
            default_profile = os.path.join(user_data_dir, "Default")
            save_profile_to_json(default_profile)
        else:
            print("\nAvailable profiles:")
            for idx, profile in enumerate(profiles, 1):
                print(f"  {idx}. {profile['name']}")
            
            while True:
                try:
                    choice = input(f"\nSelect profile (1-{len(profiles)}): ")
                    choice_idx = int(choice) - 1
                    
                    if 0 <= choice_idx < len(profiles):
                        selected_profile = profiles[choice_idx]['path']
                        save_profile_to_json(selected_profile)
                        break
                    else:
                        print("❌ Invalid choice. Please try again.")
                except ValueError:
                    print("❌ Please enter a valid number.")
                except KeyboardInterrupt:
                    print("\n\n❌ Setup cancelled by user")
                    return
    
    # Validate the configuration
    print("\n" + "=" * 60)
    print("Validating configuration...")
    print("=" * 60)
    
    if validate_chrome_config():
        print("\n" + "=" * 60)
        print("✅ SETUP COMPLETE AND VALIDATED!")
        print("=" * 60)
        print("\n🎉 You're all set! You can now:")
        print("   1. Run 'python main.py' to start the voice assistant")
        print("   2. Use voice command: 'start form filling'")
        print("   3. Use voice command: 'send whatsapp message'")
        print("   4. All Chrome automations are ready!")
        print("\n" + "=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠️  SETUP COMPLETED BUT VALIDATION FAILED")
        print("=" * 60)
        print("\n❌ There were errors in the configuration.")
        print("   Please run setup again or manually check chrome_profile.json")
        print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error during setup: {e}")
        import traceback
        traceback.print_exc()
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
    """Save the selected profile path to a JSON file"""
    data = {
        "profile_path": profile_path,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"\n✓ Profile path saved to {filename}")
    print(f"  Profile: {profile_path}")

def open_chrome_profile_selector():
    """Open Chrome with profile selector"""
    chrome_path = find_chrome_executable()
    
    if not chrome_path:
        print("Error: Chrome executable not found!")
        print("Please install Google Chrome or provide the correct path.")
        return None
    
    print(f"Found Chrome at: {chrome_path}")
    
    user_data_dir = get_chrome_user_data_dir()
    print(f"Chrome User Data Directory: {user_data_dir}")
    
    # Get existing profiles
    profiles = get_chrome_profiles(user_data_dir)
    
    if profiles:
        print(f"\nFound {len(profiles)} existing profile(s):")
        for idx, profile in enumerate(profiles, 1):
            print(f"  {idx}. {profile['name']}")
    else:
        print("\nNo existing profiles found.")
    
    print("\nOpening Chrome Profile Selector...")
    print("Please select a profile or create a new one in Chrome.")
    print("After selecting/creating a profile, return here and press Enter.")
    
    # Open Chrome with profile picker
    # The --profile-directory flag with an empty value shows the profile picker
    try:
        subprocess.Popen([chrome_path, "--profile-directory="])
        print("\n✓ Chrome opened successfully!")
    except Exception as e:
        print(f"Error opening Chrome: {e}")
        return None
    
    # Wait for user to select profile
    input("\nPress Enter after you've selected or created a profile in Chrome...")
    
    return user_data_dir

def detect_active_chrome_profile(user_data_dir):
    """Detect which Chrome profile is currently active"""
    try:
        # Look for Chrome processes and their command line arguments
        for proc in psutil.process_iter(['name', 'cmdline']):
            if proc.info['name'] and 'chrome.exe' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline:
                    for arg in cmdline:
                        if '--profile-directory=' in arg:
                            profile_name = arg.split('--profile-directory=')[1]
                            profile_path = os.path.join(user_data_dir, profile_name)
                            return profile_path
        
        # If no specific profile found, assume Default
        default_profile = os.path.join(user_data_dir, "Default")
        if os.path.exists(default_profile):
            return default_profile
            
    except Exception as e:
        print(f"Error detecting active profile: {e}")
    
    return None

def main():
    print("=" * 60)
    print("Chrome Profile Setup")
    print("=" * 60)
    
    user_data_dir = open_chrome_profile_selector()
    
    if not user_data_dir:
        return
    
    print("\nDetecting selected profile...")
    time.sleep(2)  # Give Chrome time to start
    
    profile_path = detect_active_chrome_profile(user_data_dir)
    
    if profile_path:
        save_profile_to_json(profile_path)
    else:
        print("\nCouldn't automatically detect the profile.")
        print("Listing available profiles:")
        
        profiles = get_chrome_profiles(user_data_dir)
        
        if not profiles:
            print("No profiles found. Using default profile path.")
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
                        print("Invalid choice. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
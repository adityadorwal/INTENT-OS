"""
Auto Form Filler Launcher
- Opens Tkinter window to paste Google Form URL
- Handles smart Chrome tab management (NEW TAB in existing Chrome)
- NEVER closes other Chrome profiles
- Uses chrome_profile.json for configuration
"""

import tkinter as tk
from tkinter import messagebox
import json
import os
import subprocess
import sys
import time
import psutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


class FormFillerLauncher:
    def __init__(self):
        """Initialize the launcher"""
        self.load_chrome_config()
        self.setup_ui()
    
    def load_chrome_config(self):
        """Load Chrome profile configuration from chrome_profile.json"""
        try:
            # Look for chrome_profile.json in parent directory
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chrome_profile.json")
            
            if not os.path.exists(config_path):
                # Try current directory
                config_path = "chrome_profile.json"
            
            if not os.path.exists(config_path):
                raise FileNotFoundError("chrome_profile.json not found!")
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Extract form filler settings
            self.profile_path = config['form_filler']['profile_path']
            self.debug_port = config['form_filler']['debug_port']
            
            print(f"✅ Chrome profile loaded: {self.profile_path}")
            print(f"✅ Debug port: {self.debug_port}")
            
        except Exception as e:
            print(f"❌ Error loading Chrome config: {e}")
            self.profile_path = None
            self.debug_port = 9222
    
    def setup_ui(self):
        """Create the Tkinter launcher window"""
        self.root = tk.Tk()
        self.root.title("Auto Form Filler")
        self.root.geometry("500x200")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Header
        header = tk.Label(
            self.root, 
            text="🤖 Auto Form Filler", 
            font=("Arial", 16, "bold"),
            pady=15
        )
        header.pack()
        
        # URL input frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(
            input_frame, 
            text="Paste Google Form URL:", 
            font=("Arial", 10)
        ).pack(anchor='w')
        
        self.url_entry = tk.Entry(input_frame, font=("Arial", 10), width=50)
        self.url_entry.pack(pady=5, fill='x')
        self.url_entry.focus()
        
        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)
        
        self.fill_button = tk.Button(
            button_frame,
            text="🚀 Fill Form",
            command=self.launch_form_filler,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.fill_button.pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="❌ Cancel",
            command=self.root.destroy,
            bg="#f44336",
            fg="white",
            font=("Arial", 12),
            padx=20,
            pady=10,
            cursor="hand2"
        ).pack(side="left", padx=5)
        
        # Bind Enter key
        self.url_entry.bind('<Return>', lambda e: self.launch_form_filler())
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def is_chrome_running_with_profile(self):
        """
        Check if Chrome is already running with our profile
        IMPORTANT: Does NOT close any Chrome instances!
        """
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline:
                        cmdline_str = ' '.join(cmdline)
                        # Check if our profile is in use
                        if self.profile_path and self.profile_path.replace('\\', '/') in cmdline_str.replace('\\', '/'):
                            print(f"✅ Chrome already running with our profile (PID: {proc.info['pid']})")
                            return True
            
            print("ℹ️ Chrome not running with our profile")
            return False
            
        except Exception as e:
            print(f"⚠️ Error checking Chrome processes: {e}")
            return False
    
    def start_chrome_with_debugging(self):
        """
        Start Chrome with remote debugging enabled
        CRITICAL: Does NOT close existing Chrome instances!
        """
        try:
            print(f"\n🚀 Starting Chrome with debugging...")
            print(f"Profile: {self.profile_path}")
            print(f"Debug port: {self.debug_port}")
            
            # Chrome executable paths (try common locations)
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser"
            ]
            
            chrome_exe = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_exe = path
                    break
            
            if not chrome_exe:
                raise FileNotFoundError("Chrome executable not found!")
            
            # Build command - IMPORTANT: This creates a NEW window, doesn't close others
            cmd = [
                chrome_exe,
                f"--remote-debugging-port={self.debug_port}",
                f"--user-data-dir={self.profile_path}"
            ]
            
            # Start Chrome in background (detached process)
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
            
            print("✅ Chrome started with debugging enabled")
            time.sleep(3)  # Wait for Chrome to initialize
            
            return True
            
        except Exception as e:
            print(f"❌ Error starting Chrome: {e}")
            return False
    
    def open_form_in_chrome(self, url):
        """
        Open form URL in Chrome using Selenium
        Will open in NEW TAB if Chrome is already running
        """
        try:
            print(f"\n🌐 Opening form: {url}")
            
            # Setup Chrome options for connecting to existing instance
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.debug_port}")
            
            # Connect to Chrome
            print(f"🔌 Connecting to Chrome on port {self.debug_port}...")
            driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate directly to the URL (don't use window.open)
            print("📂 Opening form...")
            driver.get(url)
            
            # Wait for form to load
            print("⏳ Waiting for form to load...")
            time.sleep(2)
            
            print("✅ Form opened successfully!")
            print("🤖 Auto-filling will begin shortly...\n")
            
            # IMPORTANT: Don't quit the driver - keep it alive for the core script
            # The core script will connect to the same Chrome instance
            return True
            
        except Exception as e:
            print(f"❌ Error opening form: {e}")
            messagebox.showerror(
                "Error",
                f"Failed to open form in Chrome:\n{str(e)}\n\n"
                "Make sure Chrome is running with debugging enabled."
            )
            return False
    
    def launch_form_filler(self):
        """Main launch function - coordinates everything"""
        # Get URL
        url = self.url_entry.get().strip()
        
        # Validate URL
        if not url:
            messagebox.showwarning("No URL", "Please paste a Google Form URL!")
            return
        
        if "docs.google.com/forms" not in url:
            messagebox.showwarning(
                "Invalid URL", 
                "Please paste a valid Google Form URL!\n\n"
                "Example: https://docs.google.com/forms/d/xyz/viewform"
            )
            return
        
        # Disable button to prevent double-click
        self.fill_button.config(state='disabled', text="Launching...")
        self.root.update()
        
        try:
            # Check if Chrome is already running with our profile
            chrome_running = self.is_chrome_running_with_profile()
            
            if not chrome_running:
                # Start Chrome with debugging
                print("\n" + "="*60)
                print("Chrome not running - starting with debugging enabled...")
                print("="*60)
                
                if not self.start_chrome_with_debugging():
                    raise Exception("Failed to start Chrome")
            else:
                print("\n" + "="*60)
                print("Chrome already running - will open in new tab")
                print("="*60)
            
            # Open form in Chrome (new tab)
            if self.open_form_in_chrome(url):
                # Success - close launcher window
                messagebox.showinfo(
                    "Success",
                    "Form opened successfully!\n\n"
                    "Auto-filling will begin shortly..."
                )
                
                # Start the auto filler core
                self.start_auto_filler_core()
                
                # Close launcher window
                self.root.destroy()
            else:
                # Failed - re-enable button
                self.fill_button.config(state='normal', text="🚀 Fill Form")
        
        except Exception as e:
            print(f"❌ Launch failed: {e}")
            messagebox.showerror(
                "Launch Failed",
                f"Failed to launch form filler:\n{str(e)}"
            )
            self.fill_button.config(state='normal', text="🚀 Fill Form")
    
    def start_auto_filler_core(self):
        """Start the auto_form_filler_core.py in background"""
        try:
            # Path to auto_form_filler_core.py
            core_path = os.path.join(
                os.path.dirname(__file__), 
                "auto_form_filler_core.py"
            )
            
            if not os.path.exists(core_path):
                print(f"⚠️ auto_form_filler_core.py not found at: {core_path}")
                print("⚠️ Make sure it's in the same directory!")
                return
            
            # Start in background with proper error handling
            print(f"\n🚀 Starting auto_form_filler_core.py...")
            
            # Add a small delay to ensure Chrome is ready
            time.sleep(2)
            
            if os.name == 'nt':  # Windows
                # Create a batch file to keep console open on error
                batch_content = f'''@echo off
echo Starting Auto Form Filler Core...
python "{core_path}"
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Form filler encountered an error
    echo ========================================
    echo.
    pause
) else (
    echo.
    echo Form filling completed successfully!
    timeout /t 3
)
'''
                batch_path = os.path.join(os.path.dirname(core_path), "run_core.bat")
                with open(batch_path, 'w') as f:
                    f.write(batch_content)
                
                subprocess.Popen(
                    ['cmd', '/c', batch_path],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:  # Linux/Mac
                subprocess.Popen(['python3', core_path])
            
            print("✅ Auto filler core started!")
            
        except Exception as e:
            print(f"⚠️ Could not start auto filler core: {e}")
            print("⚠️ You may need to run auto_form_filler_core.py manually")
    
    def run(self):
        """Run the launcher"""
        self.root.mainloop()


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🤖 AUTO FORM FILLER LAUNCHER")
    print("="*60)
    print("✅ Ready to launch!")
    print("="*60 + "\n")
    
    launcher = FormFillerLauncher()
    launcher.run()


if __name__ == "__main__":
    main()
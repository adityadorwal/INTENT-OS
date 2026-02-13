"""
GUI Setup for Intent OS
Ek hi window mein sab kuch - requirements, API keys, configuration
"""

import sys
import os
import json
import subprocess
import threading
from pathlib import Path
from tkinter import *
from tkinter import ttk, messagebox, scrolledtext
from tkinter.font import Font

class IntentOSSetup:
    def __init__(self):
        self.root = Tk()
        self.root.title("Intent OS - Setup Wizard")
        self.root.geometry("900x700")  # Made taller to show all buttons
        self.root.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Variables
        self.current_step = 0
        self.steps = [
            "Requirements Check",
            "Install Dependencies", 
            "API Keys Setup",
            "Chrome Configuration",
            "Form Filler Data",
            "Final Setup"
        ]
        
        self.api_keys = {
            'groq': StringVar(),
            'gemini': StringVar(),
            'deepseek': StringVar()
        }
        
        self.personal_data = {
            'first_name': StringVar(),
            'last_name': StringVar(),
            'email': StringVar(),
            'phone': StringVar(),
            'address': StringVar(),
            'city': StringVar()
        }
        
        self.setup_ui()
        
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Setup main UI"""
        # Header
        header_frame = Frame(self.root, bg='#2c3e50', height=100)
        header_frame.pack(fill=X)
        header_frame.pack_propagate(False)
        
        title_font = Font(family="Arial", size=24, weight="bold")
        title_label = Label(
            header_frame, 
            text="🎤 Intent OS Setup Wizard",
            font=title_font,
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=10)
        
        subtitle_label = Label(
            header_frame,
            text="Complete setup in 6 easy steps - No CMD needed!",
            font=("Arial", 11),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        subtitle_label.pack()
        
        # Progress bar
        progress_frame = Frame(self.root, bg='#ecf0f1', height=60)
        progress_frame.pack(fill=X)
        progress_frame.pack_propagate(False)
        
        self.progress = ttk.Progressbar(
            progress_frame, 
            length=700, 
            mode='determinate',
            maximum=len(self.steps)
        )
        self.progress.pack(pady=15)
        
        self.progress_label = Label(
            progress_frame,
            text=f"Step 1 of {len(self.steps)}: {self.steps[0]}",
            bg='#ecf0f1',
            font=("Arial", 10, "bold")
        )
        self.progress_label.pack()
        
        # Main content area
        self.content_frame = Frame(self.root, bg='white')
        self.content_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Button frame
        button_frame = Frame(self.root, bg='#ecf0f1', height=70)
        button_frame.pack(fill=X)
        button_frame.pack_propagate(False)
        
        self.prev_btn = Button(
            button_frame,
            text="← Previous",
            command=self.prev_step,
            state=DISABLED,
            bg='#95a5a6',
            fg='white',
            font=("Arial", 11, "bold"),
            padx=25,
            pady=8
        )
        self.prev_btn.pack(side=LEFT, padx=20, pady=15)
        
        self.next_btn = Button(
            button_frame,
            text="Next →",
            command=self.next_step,
            bg='#3498db',
            fg='white',
            font=("Arial", 11, "bold"),
            padx=25,
            pady=8
        )
        self.next_btn.pack(side=RIGHT, padx=20, pady=15)
        
        # Start with first step
        self.show_step()
    
    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_step(self):
        """Show current step"""
        self.clear_content()
        self.progress['value'] = self.current_step + 1
        self.progress_label.config(
            text=f"Step {self.current_step + 1} of {len(self.steps)}: {self.steps[self.current_step]}"
        )
        
        if self.current_step == 0:
            self.show_requirements_check()
        elif self.current_step == 1:
            self.show_install_dependencies()
        elif self.current_step == 2:
            self.show_api_keys()
        elif self.current_step == 3:
            self.show_chrome_config()
        elif self.current_step == 4:
            self.show_form_data()
        elif self.current_step == 5:
            self.show_final_setup()
    
    def show_requirements_check(self):
        """Step 1: Check requirements"""
        Label(
            self.content_frame,
            text="System Requirements Check",
            font=("Arial", 16, "bold"),
            bg='white'
        ).pack(pady=20)
        
        # Check results frame
        self.check_frame = Frame(self.content_frame, bg='white')
        self.check_frame.pack(fill=BOTH, expand=True)
        
        # Start checking
        self.check_requirements()
    
    def check_requirements(self):
        """Check system requirements"""
        checks = [
            ("Python Version", self.check_python),
            ("Internet Connection", self.check_internet),
            ("Write Permissions", self.check_permissions),
            ("Microphone Access", self.check_microphone)
        ]
        
        for i, (name, check_func) in enumerate(checks):
            result_frame = Frame(self.check_frame, bg='white')
            result_frame.pack(fill=X, pady=5)
            
            Label(
                result_frame,
                text=f"{name}:",
                font=("Arial", 12),
                bg='white',
                width=20,
                anchor='w'
            ).pack(side=LEFT)
            
            # Run check
            try:
                success, message = check_func()
                if success:
                    Label(
                        result_frame,
                        text="✅ " + message,
                        font=("Arial", 12),
                        bg='white',
                        fg='green'
                    ).pack(side=LEFT)
                else:
                    Label(
                        result_frame,
                        text="❌ " + message,
                        font=("Arial", 12),
                        bg='white',
                        fg='red'
                    ).pack(side=LEFT)
            except Exception as e:
                Label(
                    result_frame,
                    text=f"❌ Error: {e}",
                    font=("Arial", 12),
                    bg='white',
                    fg='red'
                ).pack(side=LEFT)
    
    def check_python(self):
        """Check Python version"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            return True, f"Python {version.major}.{version.minor}.{version.micro}"
        else:
            return False, f"Python {version.major}.{version.minor} (Need 3.8+)"
    
    def check_internet(self):
        """Check internet connection"""
        try:
            import urllib.request
            urllib.request.urlopen('https://www.google.com', timeout=5)
            return True, "Connected"
        except:
            return False, "No connection"
    
    def check_permissions(self):
        """Check write permissions"""
        try:
            test_file = Path('.test_write')
            test_file.write_text('test')
            test_file.unlink()
            return True, "Can write files"
        except:
            return False, "Cannot write files"
    
    def check_microphone(self):
        """Check microphone (basic check)"""
        try:
            import pyaudio
            return True, "PyAudio available"
        except ImportError:
            return False, "PyAudio not installed"
        except:
            return True, "Microphone check skipped"
    
    def show_install_dependencies(self):
        """Step 2: Install dependencies"""
        Label(
            self.content_frame,
            text="Install Required Packages",
            font=("Arial", 16, "bold"),
            bg='white'
        ).pack(pady=20)
        
        Label(
            self.content_frame,
            text="Installing Python packages needed for Intent OS...",
            font=("Arial", 12),
            bg='white'
        ).pack(pady=10)
        
        # Progress text area
        self.install_text = scrolledtext.ScrolledText(
            self.content_frame,
            height=15,
            width=80,
            font=("Consolas", 9)
        )
        self.install_text.pack(fill=BOTH, expand=True, pady=10)
        
        # Install button
        self.install_btn = Button(
            self.content_frame,
            text="🚀 Install All Packages",
            command=self.install_packages,
            bg='#2ecc71',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10
        )
        self.install_btn.pack(pady=10)
        
        # Skip button (if packages already installed)
        skip_btn = Button(
            self.content_frame,
            text="⏭️ Skip (Already Installed)",
            command=self.skip_installation,
            bg='#95a5a6',
            fg='white',
            font=("Arial", 10),
            padx=20,
            pady=5
        )
        skip_btn.pack(pady=5)
    
    def install_packages(self):
        """Install all required packages"""
        packages = [
            'PyQt5',
            'selenium', 
            'SpeechRecognition',
            'PyAudio',
            'psutil',
            'requests',
            'python-dotenv',
            'pyttsx3'
        ]
        
        self.install_btn.config(state=DISABLED, text="Installing...")
        self.next_btn.config(state=DISABLED)  # Disable Next during installation
        self.install_text.delete(1.0, END)
        
        def install_thread():
            for package in packages:
                self.install_text.insert(END, f"Installing {package}...\n")
                self.install_text.see(END)
                self.root.update()
                
                try:
                    result = subprocess.run(
                        [sys.executable, '-m', 'pip', 'install', package],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    if result.returncode == 0:
                        self.install_text.insert(END, f"✅ {package} installed successfully\n")
                    else:
                        self.install_text.insert(END, f"❌ {package} failed: {result.stderr}\n")
                except subprocess.TimeoutExpired:
                    self.install_text.insert(END, f"⏰ {package} installation timeout\n")
                except Exception as e:
                    self.install_text.insert(END, f"❌ {package} error: {e}\n")
                
                self.install_text.see(END)
                self.root.update()
            
            self.install_text.insert(END, "\n🎉 Installation complete!\n")
            self.install_text.insert(END, "\n" + "="*60 + "\n")
            self.install_text.insert(END, "💡 IMPORTANT: Look for the GREEN 'Next →' button\n")
            self.install_text.insert(END, "   at the BOTTOM RIGHT of this window!\n")
            self.install_text.insert(END, "="*60 + "\n")
            self.install_text.see(END)
            
            # Re-enable buttons
            self.install_btn.config(state=NORMAL, text="✅ Installation Done", bg='#27ae60')
            self.next_btn.config(state=NORMAL, bg='#2ecc71', font=("Arial", 12, "bold"))  # Bigger font
            
            # Flash the Next button to draw attention
            def flash_button(count=0):
                if count < 6:  # Flash 3 times
                    current_bg = self.next_btn.cget('bg')
                    new_bg = '#f39c12' if current_bg == '#2ecc71' else '#2ecc71'  # Orange/Green
                    self.next_btn.config(bg=new_bg)
                    self.root.after(300, lambda: flash_button(count + 1))
            
            flash_button()
            self.root.update()
        
        # Run in thread
        thread = threading.Thread(target=install_thread)
        thread.daemon = True
        thread.start()
    
    def skip_installation(self):
        """Skip package installation"""
        self.install_text.delete(1.0, END)
        self.install_text.insert(END, "⏭️ Skipping package installation...\n")
        self.install_text.insert(END, "\n💡 Make sure all packages are already installed!\n")
        self.install_text.insert(END, "\n✅ Click 'Next' to continue...\n")
        
        self.install_btn.config(state=DISABLED, text="✅ Skipped")
        self.next_btn.config(state=NORMAL, bg='#2ecc71')
    
    def show_api_keys(self):
        """Step 3: API Keys setup"""
        Label(
            self.content_frame,
            text="API Keys Configuration",
            font=("Arial", 16, "bold"),
            bg='white'
        ).pack(pady=20)
        
        Label(
            self.content_frame,
            text="Enter at least one API key for AI features:",
            font=("Arial", 12),
            bg='white'
        ).pack(pady=10)
        
        # API key entries
        api_frame = Frame(self.content_frame, bg='white')
        api_frame.pack(fill=X, pady=20)
        
        apis = [
            ('groq', 'Groq API Key', 'gsk_...'),
            ('gemini', 'Google Gemini API Key', 'AIza...'),
            ('deepseek', 'DeepSeek API Key', 'sk-...')
        ]
        
        for key, label, placeholder in apis:
            row = Frame(api_frame, bg='white')
            row.pack(fill=X, pady=5)
            
            Label(
                row,
                text=label + ":",
                font=("Arial", 11),
                bg='white',
                width=20,
                anchor='w'
            ).pack(side=LEFT)
            
            entry = Entry(
                row,
                textvariable=self.api_keys[key],
                font=("Arial", 11),
                width=50,
                show='*'
            )
            entry.pack(side=LEFT, padx=10)
            entry.insert(0, placeholder)
            entry.bind('<FocusIn>', lambda e, ph=placeholder: self.clear_placeholder(e, ph))
        
        # Info
        info_text = """
💡 How to get API keys:
• Groq: https://console.groq.com/keys (Recommended - Fast & Free)
• Gemini: https://makersuite.google.com/app/apikey
• DeepSeek: https://platform.deepseek.com/api_keys

You need at least one API key for voice commands to work.
        """
        
        Label(
            self.content_frame,
            text=info_text,
            font=("Arial", 10),
            bg='white',
            justify=LEFT,
            fg='#7f8c8d'
        ).pack(pady=20)
    
    def clear_placeholder(self, event, placeholder):
        """Clear placeholder text"""
        if event.widget.get() == placeholder:
            event.widget.delete(0, END)
    
    def show_chrome_config(self):
        """Step 4: Chrome configuration"""
        Label(
            self.content_frame,
            text="Chrome Configuration",
            font=("Arial", 16, "bold"),
            bg='white'
        ).pack(pady=20)
        
        Label(
            self.content_frame,
            text="Setting up Chrome for form filling and WhatsApp automation...",
            font=("Arial", 12),
            bg='white'
        ).pack(pady=10)
        
        # Auto-detect Chrome
        chrome_frame = Frame(self.content_frame, bg='white')
        chrome_frame.pack(fill=X, pady=20)
        
        self.chrome_path = self.find_chrome()
        
        Label(
            chrome_frame,
            text="Chrome Location:",
            font=("Arial", 11, "bold"),
            bg='white'
        ).pack(anchor=W)
        
        Label(
            chrome_frame,
            text=self.chrome_path if self.chrome_path else "Chrome not found",
            font=("Arial", 10),
            bg='white',
            fg='green' if self.chrome_path else 'red'
        ).pack(anchor=W, pady=5)
        
        if self.chrome_path:
            Label(
                chrome_frame,
                text="✅ Chrome configuration will be set up automatically",
                font=("Arial", 11),
                bg='white',
                fg='green'
            ).pack(anchor=W, pady=10)
        else:
            Label(
                chrome_frame,
                text="⚠️ Chrome not found. Some features may not work.",
                font=("Arial", 11),
                bg='white',
                fg='orange'
            ).pack(anchor=W, pady=10)
    
    def find_chrome(self):
        """Find Chrome installation"""
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/usr/bin/google-chrome"
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        return None
    
    def show_form_data(self):
        """Step 5: Form filler personal data"""
        Label(
            self.content_frame,
            text="Personal Information for Form Filling",
            font=("Arial", 16, "bold"),
            bg='white'
        ).pack(pady=20)
        
        Label(
            self.content_frame,
            text="This data will be used to automatically fill forms (stored locally):",
            font=("Arial", 12),
            bg='white'
        ).pack(pady=10)
        
        # Personal data form
        data_frame = Frame(self.content_frame, bg='white')
        data_frame.pack(fill=X, pady=20)
        
        fields = [
            ('first_name', 'First Name'),
            ('last_name', 'Last Name'),
            ('email', 'Email Address'),
            ('phone', 'Phone Number'),
            ('address', 'Address'),
            ('city', 'City')
        ]
        
        for key, label in fields:
            row = Frame(data_frame, bg='white')
            row.pack(fill=X, pady=5)
            
            Label(
                row,
                text=label + ":",
                font=("Arial", 11),
                bg='white',
                width=15,
                anchor='w'
            ).pack(side=LEFT)
            
            Entry(
                row,
                textvariable=self.personal_data[key],
                font=("Arial", 11),
                width=40
            ).pack(side=LEFT, padx=10)
        
        Label(
            self.content_frame,
            text="💡 This information is optional but helps with automatic form filling",
            font=("Arial", 10),
            bg='white',
            fg='#7f8c8d'
        ).pack(pady=20)
    
    def show_final_setup(self):
        """Step 6: Final setup"""
        Label(
            self.content_frame,
            text="Final Setup",
            font=("Arial", 16, "bold"),
            bg='white'
        ).pack(pady=20)
        
        Label(
            self.content_frame,
            text="Creating configuration files...",
            font=("Arial", 12),
            bg='white'
        ).pack(pady=10)
        
        # Setup progress
        self.setup_text = scrolledtext.ScrolledText(
            self.content_frame,
            height=10,
            width=80,
            font=("Consolas", 9)
        )
        self.setup_text.pack(fill=BOTH, expand=True, pady=10)
        
        # Finish button
        self.finish_btn = Button(
            self.content_frame,
            text="🎉 Complete Setup",
            command=self.complete_setup,
            bg='#2ecc71',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10
        )
        self.finish_btn.pack(pady=10)
    
    def complete_setup(self):
        """Complete the setup process"""
        self.finish_btn.config(state=DISABLED, text="Setting up...")
        self.setup_text.delete(1.0, END)
        
        def setup_thread():
            # Create .env file
            self.setup_text.insert(END, "Creating .env file...\n")
            self.create_env_file()
            
            # Create Chrome config
            self.setup_text.insert(END, "Creating Chrome configuration...\n")
            self.create_chrome_config()
            
            # Create form filler data
            self.setup_text.insert(END, "Creating form filler data...\n")
            self.create_form_data()
            
            # Create setup complete flag
            self.setup_text.insert(END, "Marking setup as complete...\n")
            Path('.setup_complete').touch()
            
            self.setup_text.insert(END, "\n🎉 Setup completed successfully!\n")
            self.setup_text.insert(END, "\nYou can now:\n")
            self.setup_text.insert(END, "• Double-click START_HERE.bat\n")
            self.setup_text.insert(END, "• Or run: python run.py\n")
            
            self.finish_btn.config(
                state=NORMAL, 
                text="🚀 Launch Intent OS",
                command=self.launch_intent_os
            )
        
        thread = threading.Thread(target=setup_thread)
        thread.daemon = True
        thread.start()
    
    def create_env_file(self):
        """Create .env file with API keys"""
        env_content = []
        
        for key, var in self.api_keys.items():
            value = var.get().strip()
            if value and not value.startswith(('gsk_', 'AIza', 'sk-')):
                continue  # Skip placeholder text
            if value:
                env_content.append(f"{key.upper()}_API_KEY={value}")
        
        if env_content:
            with open('.env', 'w') as f:
                f.write('\n'.join(env_content))
            self.setup_text.insert(END, "✅ API keys saved\n")
        else:
            self.setup_text.insert(END, "⚠️ No valid API keys provided\n")
        
        self.root.update()
    
    def create_chrome_config(self):
        """Create Chrome configuration"""
        if self.chrome_path:
            profile_path = os.path.expanduser("~/AppData/Local/Google/Chrome/User Data/Default")
            config = {
                "chrome_profiles": {
                    "whatsapp_profile": profile_path,
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
                }
            }
            
            with open('chrome_profile.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            self.setup_text.insert(END, "✅ Chrome configuration created\n")
        else:
            self.setup_text.insert(END, "⚠️ Chrome not found, skipping config\n")
        
        self.root.update()
    
    def create_form_data(self):
        """Create form filler data"""
        data = {
            "personal_info": {},
            "education": {},
            "professional": {},
            "learned_questions": {},
            "preferences": {
                "auto_fill_enabled": True,
                "learn_new_questions": True
            }
        }
        
        # Add personal data
        for key, var in self.personal_data.items():
            value = var.get().strip()
            if value:
                data["personal_info"][key] = value
        
        # Ensure directory exists
        os.makedirs('Auto_Form_Filler', exist_ok=True)
        
        with open('Auto_Form_Filler/user_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        self.setup_text.insert(END, "✅ Form filler data created\n")
        self.root.update()
    
    def launch_intent_os(self):
        """Launch Intent OS"""
        try:
            subprocess.Popen([sys.executable, 'run.py'])
            messagebox.showinfo(
                "Success",
                "Intent OS is starting!\n\nLook for the floating microphone button."
            )
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch: {e}")
    
    def next_step(self):
        """Go to next step"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.show_step()
            
            # Update buttons
            self.prev_btn.config(state=NORMAL)
            self.next_btn.config(bg='#3498db')  # Reset to blue
            
            if self.current_step == len(self.steps) - 1:
                self.next_btn.config(text="Finish", state=DISABLED)
    
    def prev_step(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.show_step()
            
            # Update buttons
            if self.current_step == 0:
                self.prev_btn.config(state=DISABLED)
            self.next_btn.config(text="Next →", state=NORMAL)
    
    def run(self):
        """Run the setup wizard"""
        self.root.mainloop()

if __name__ == "__main__":
    print("🚀 Starting Intent OS Setup Wizard...")
    setup = IntentOSSetup()
    setup.run()
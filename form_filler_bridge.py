"""
Form Filler Bridge - Voice Command Integration
Connects Auto Form Filler to Intent_OS for voice-controlled form filling
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

# Import logging
from logger_config import get_logger

logger = get_logger("form_filler_bridge")


class FormFillerBridge:
    """
    Bridge between Intent_OS and Auto Form Filler
    Provides voice-controlled access to auto form filling functionality
    """
    
    def __init__(self):
        """Initialize the Form Filler Bridge"""
        self.form_filler_dir = Path(__file__).parent / "Auto_Form_Filler"
        self.user_data_path = self.form_filler_dir / "user_data.json"
        self.launcher_path = self.form_filler_dir / "form_filler_launcher.py"
        self.core_path = self.form_filler_dir / "auto_form_filler_core.py"
        
        # Check if Auto_Form_Filler exists
        if not self.form_filler_dir.exists():
            logger.warning("Auto_Form_Filler directory not found!")
            print("⚠️  Auto_Form_Filler directory not found!")
        else:
            logger.info("Form Filler Bridge initialized")
            print("🤖 Form Filler Bridge ready!")
    
    def is_available(self) -> bool:
        """
        Check if Auto Form Filler is available
        
        Returns:
            bool: True if all required files exist
        """
        if not self.form_filler_dir.exists():
            return False
            
        required_files = [
            self.launcher_path,
            self.core_path
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                logger.warning(f"Missing required file: {file_path}")
                print(f"⚠️  Missing: {file_path.name}")
                return False
        
        logger.info("All Form Filler files present")
        return True
    
    def start_form_filler(self) -> bool:
        """
        Launch the Auto Form Filler UI
        
        This opens the Tkinter window where users can paste Google Form URLs
        
        Returns:
            bool: True if launched successfully
        """
        try:
            logger.info("Starting Form Filler launcher...")
            print("\n🤖 Starting Auto Form Filler...")
            
            # Check availability
            if not self.is_available():
                logger.error("Form Filler not available - missing files")
                print("❌ Auto Form Filler is not properly set up!")
                print("💡 Make sure Auto_Form_Filler folder has all required files")
                return False
            
            # Launch the form filler launcher in a new process
            if os.name == 'nt':  # Windows
                subprocess.Popen(
                    [sys.executable, str(self.launcher_path)],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    cwd=str(self.form_filler_dir)
                )
            else:  # Linux/Mac
                subprocess.Popen(
                    [sys.executable, str(self.launcher_path)],
                    cwd=str(self.form_filler_dir)
                )
            
            logger.info("Form Filler launcher started successfully")
            print("✅ Auto Form Filler launcher opened!")
            print("📝 Paste your Google Form URL in the window")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Form Filler: {e}", exc_info=True)
            print(f"❌ Failed to start Auto Form Filler: {e}")
            return False
    
    def stop_form_filler(self) -> bool:
        """
        Stop/close the form filler (graceful shutdown)
        
        Returns:
            bool: True if stopped successfully
        """
        try:
            logger.info("Stopping Form Filler...")
            print("🛑 Stopping Auto Form Filler...")
            
            # Try to find and close form filler processes
            import psutil
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any('form_filler' in str(arg).lower() for arg in cmdline):
                        logger.info(f"Terminating form filler process (PID: {proc.info['pid']})")
                        proc.terminate()
                        proc.wait(timeout=3)
                        print(f"✅ Form filler process stopped (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    pass
            
            logger.info("Form Filler stopped")
            print("✅ Auto Form Filler stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping Form Filler: {e}")
            print(f"❌ Error stopping Form Filler: {e}")
            return False
    
    def get_user_data(self) -> Dict[str, Any]:
        """
        Get current user data from user_data.json
        
        Returns:
            dict: User data dictionary
        """
        try:
            if not self.user_data_path.exists():
                logger.warning("user_data.json not found")
                
                # Check for example file
                example_path = self.form_filler_dir / "user_data.example.json"
                if example_path.exists():
                    print("ℹ️  user_data.json not found, but user_data.example.json exists")
                    print("💡 Copy user_data.example.json to user_data.json and fill in your details")
                
                return {}
            
            with open(self.user_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info("User data loaded successfully")
            return data
            
        except Exception as e:
            logger.error(f"Error loading user data: {e}", exc_info=True)
            print(f"❌ Error loading user data: {e}")
            return {}
    
    def update_user_data(self, **kwargs) -> bool:
        """
        Update user data for form filling
        
        Args:
            **kwargs: Field-value pairs to update
        
        Returns:
            bool: True if updated successfully
        """
        try:
            logger.info(f"Updating user data with: {list(kwargs.keys())}")
            print(f"\n📝 Updating form filler data...")
            
            # Load existing data
            current_data = self.get_user_data()
            
            if not current_data:
                # Create from template if doesn't exist
                example_path = self.form_filler_dir / "user_data.example.json"
                if example_path.exists():
                    import shutil
                    shutil.copy(example_path, self.user_data_path)
                    with open(self.user_data_path, 'r', encoding='utf-8') as f:
                        current_data = json.load(f)
                else:
                    current_data = {"personal_info": {}, "education": {}, "professional": {}}
            
            # Update personal_info section (most common)
            if 'personal_info' not in current_data:
                current_data['personal_info'] = {}
            
            current_data['personal_info'].update(kwargs)
            
            # Save updated data
            with open(self.user_data_path, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, indent=2, ensure_ascii=False)
            
            logger.info("User data updated successfully")
            print("✅ Form filler data updated!")
            print(f"📊 Updated fields: {', '.join(kwargs.keys())}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user data: {e}", exc_info=True)
            print(f"❌ Error updating form data: {e}")
            return False
    
    def show_user_data(self):
        """Display current user data"""
        data = self.get_user_data()
        
        if not data:
            print("📝 No user data configured yet")
            print("💡 Use voice command: 'update my form data'")
            return
        
        print("\n📊 Current Form Filler Data:")
        print("=" * 60)
        
        # Show personal info
        if 'personal_info' in data:
            print("\n🔹 Personal Information:")
            for key, value in data['personal_info'].items():
                # Mask sensitive data
                if key.lower() in ['password', 'ssn', 'credit_card']:
                    display_value = '***' + str(value)[-4:] if value else '(not set)'
                else:
                    display_value = value if value else '(not set)'
                
                print(f"  {key.replace('_', ' ').title()}: {display_value}")
        
        # Show education
        if 'education' in data:
            print("\n🔹 Education:")
            for key, value in data['education'].items():
                display_value = value if value else '(not set)'
                print(f"  {key.replace('_', ' ').title()}: {display_value}")
        
        # Show professional
        if 'professional' in data:
            print("\n🔹 Professional:")
            for key, value in data['professional'].items():
                display_value = value if value else '(not set)'
                print(f"  {key.replace('_', ' ').title()}: {display_value}")
        
        print("=" * 60)
    
    def interactive_update(self) -> bool:
        """
        Interactive mode to update user data
        Opens the user_data.json file for editing
        
        Returns:
            bool: True if file opened successfully
        """
        try:
            print("\n🤖 Opening Form Filler Data for Editing...")
            
            # Ensure user_data.json exists
            if not self.user_data_path.exists():
                example_path = self.form_filler_dir / "user_data.example.json"
                if example_path.exists():
                    import shutil
                    shutil.copy(example_path, self.user_data_path)
                    print("✅ Created user_data.json from template")
                else:
                    print("❌ user_data.example.json not found!")
                    return False
            
            # Open the file with default editor
            if sys.platform == 'win32':
                os.startfile(str(self.user_data_path))
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', str(self.user_data_path)])
            else:
                subprocess.Popen(['xdg-open', str(self.user_data_path)])
            
            print("✅ User data file opened for editing")
            print("💡 Edit your information and save the file")
            logger.info("User data file opened for editing")
            return True
            
        except Exception as e:
            logger.error(f"Error opening user data file: {e}")
            print(f"❌ Error opening file: {e}")
            print(f"💡 Manually edit: {self.user_data_path}")
            return False


# Singleton instance
_form_filler_bridge = None

def get_form_filler_bridge():
    """Get singleton instance of FormFillerBridge"""
    global _form_filler_bridge
    if _form_filler_bridge is None:
        _form_filler_bridge = FormFillerBridge()
    return _form_filler_bridge
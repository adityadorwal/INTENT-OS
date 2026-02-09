"""
System Commands Module
Provides system-level controls accessible via voice commands

Features:
- Screenshot capture
- Volume control
- System shutdown/restart/sleep (with confirmation)
- Lock screen
- System information

Usage from Intent_OS:
    from system_commands import SystemCommands
    
    sys_cmd = SystemCommands()
    sys_cmd.take_screenshot()
    sys_cmd.adjust_volume(50)
"""

import os
import sys
import platform
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import for screenshot
try:
    from PIL import ImageGrab
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False

# Import logging
from logger_config import get_logger

logger = get_logger("system_commands")


class SystemCommands:
    """
    System-level command execution
    
    Provides safe, cross-platform system controls
    """
    
    def __init__(self):
        """Initialize System Commands"""
        self.os_type = platform.system()  # 'Windows', 'Darwin' (macOS), 'Linux'
        self.screenshots_dir = Path.home() / "Pictures" / "Screenshots"
        
        # Create screenshots directory if it doesn't exist
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"System Commands initialized for {self.os_type}")
        print(f"💻 System Commands ready ({self.os_type})")
    
    # ==================== SCREENSHOT ====================
    
    def take_screenshot(self, filename: Optional[str] = None) -> bool:
        """
        Take a screenshot and save it
        
        Args:
            filename: Optional custom filename (without extension)
        
        Returns:
            bool: True if screenshot saved successfully
        """
        try:
            logger.info("Taking screenshot...")
            print("\n📸 Taking screenshot...")
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}"
            
            # Add .png extension if not present
            if not filename.endswith('.png'):
                filename += '.png'
            
            filepath = self.screenshots_dir / filename
            
            # Take screenshot based on OS
            if SCREENSHOT_AVAILABLE:
                # Use PIL (cross-platform)
                screenshot = ImageGrab.grab()
                screenshot.save(filepath)
                logger.info(f"Screenshot saved: {filepath}")
                print(f"✅ Screenshot saved: {filepath}")
                return True
            
            elif self.os_type == 'Windows':
                # Use Windows Snipping Tool or native method
                import pyautogui
                screenshot = pyautogui.screenshot()
                screenshot.save(filepath)
                logger.info(f"Screenshot saved: {filepath}")
                print(f"✅ Screenshot saved: {filepath}")
                return True
            
            elif self.os_type == 'Darwin':  # macOS
                # Use screencapture command
                subprocess.run(['screencapture', str(filepath)], check=True)
                logger.info(f"Screenshot saved: {filepath}")
                print(f"✅ Screenshot saved: {filepath}")
                return True
            
            elif self.os_type == 'Linux':
                # Use scrot or gnome-screenshot
                try:
                    subprocess.run(['scrot', str(filepath)], check=True)
                    logger.info(f"Screenshot saved: {filepath}")
                    print(f"✅ Screenshot saved: {filepath}")
                    return True
                except FileNotFoundError:
                    try:
                        subprocess.run(['gnome-screenshot', '-f', str(filepath)], check=True)
                        logger.info(f"Screenshot saved: {filepath}")
                        print(f"✅ Screenshot saved: {filepath}")
                        return True
                    except FileNotFoundError:
                        logger.error("No screenshot tool found on Linux")
                        print("❌ No screenshot tool found! Install scrot or gnome-screenshot")
                        return False
            
            else:
                logger.error(f"Screenshot not supported on {self.os_type}")
                print(f"❌ Screenshot not supported on {self.os_type}")
                return False
                
        except Exception as e:
            logger.error(f"Screenshot failed: {e}", exc_info=True)
            print(f"❌ Screenshot failed: {e}")
            return False
    
    # ==================== VOLUME CONTROL ====================
    
    def adjust_volume(self, level: int) -> bool:
        """
        Adjust system volume
        
        Args:
            level: Volume level 0-100
        
        Returns:
            bool: True if adjusted successfully
        """
        try:
            # Clamp level to 0-100
            level = max(0, min(100, level))
            
            logger.info(f"Adjusting volume to {level}%")
            print(f"\n🔊 Setting volume to {level}%...")
            
            if self.os_type == 'Windows':
                # Use nircmd or pycaw
                try:
                    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                    from ctypes import cast, POINTER
                    from comtypes import CLSCTX_ALL
                    
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(
                        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    
                    # Set volume (0.0 to 1.0)
                    volume.SetMasterVolumeLevelScalar(level / 100.0, None)
                    
                    logger.info(f"Volume set to {level}%")
                    print(f"✅ Volume set to {level}%")
                    return True
                    
                except ImportError:
                    logger.warning("pycaw not installed, volume control unavailable")
                    print("❌ Volume control requires 'pycaw' package")
                    print("💡 Install with: pip install pycaw")
                    return False
            
            elif self.os_type == 'Darwin':  # macOS
                # Use osascript
                subprocess.run([
                    'osascript', '-e',
                    f'set volume output volume {level}'
                ], check=True)
                logger.info(f"Volume set to {level}%")
                print(f"✅ Volume set to {level}%")
                return True
            
            elif self.os_type == 'Linux':
                # Use amixer
                subprocess.run([
                    'amixer', '-D', 'pulse', 'sset', 'Master',
                    f'{level}%'
                ], check=True)
                logger.info(f"Volume set to {level}%")
                print(f"✅ Volume set to {level}%")
                return True
            
            else:
                logger.error(f"Volume control not supported on {self.os_type}")
                print(f"❌ Volume control not supported on {self.os_type}")
                return False
                
        except Exception as e:
            logger.error(f"Volume adjustment failed: {e}", exc_info=True)
            print(f"❌ Volume adjustment failed: {e}")
            return False
    
    def mute_volume(self) -> bool:
        """Mute system volume"""
        return self.adjust_volume(0)
    
    def unmute_volume(self, level: int = 50) -> bool:
        """Unmute system volume to specified level"""
        return self.adjust_volume(level)
    
    # ==================== POWER MANAGEMENT ====================
    
    def _confirm_action(self, action: str, use_gui: bool = True) -> bool:
        """
        Confirm a potentially destructive action
        
        Args:
            action: Description of the action
            use_gui: Use GUI dialog for voice interface (default: True)
        
        Returns:
            bool: True if confirmed
        """
        if use_gui:
            # GUI confirmation for voice commands
            try:
                from PyQt5.QtWidgets import QMessageBox
                
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Confirm Critical Action")
                msg.setText(f"⚠️ WARNING: About to {action}")
                msg.setInformativeText("This will close all applications!\n\nAre you sure?")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg.setDefaultButton(QMessageBox.No)
                
                result = msg.exec_()
                return result == QMessageBox.Yes
                
            except ImportError:
                # Fallback to terminal if PyQt5 not available
                print("[WARNING] GUI not available, using terminal confirmation")
                use_gui = False
        
        if not use_gui:
            # Terminal confirmation (for command line use)
            print(f"\n⚠️  WARNING: About to {action}")
            print("⚠️  This will close all applications!")
            choice = input("Are you sure? (yes/no): ").strip().lower()
            return choice in ['yes', 'y']
    
    def shutdown(self, delay: int = 60, force: bool = False, gui_mode: bool = True) -> bool:
        """
        Shutdown the computer
        
        Args:
            delay: Delay in seconds before shutdown (default: 60)
            force: Force shutdown without saving (default: False)
            gui_mode: Use GUI dialog instead of terminal input (default: True)
        
        Returns:
            bool: True if shutdown initiated
        """
        try:
            # Confirm action
            if not force and not self._confirm_action("shutdown the computer", use_gui=gui_mode):
                logger.info("Shutdown cancelled by user")
                print("❌ Shutdown cancelled")
                return False
            
            logger.warning(f"Initiating shutdown in {delay} seconds")
            print(f"\n🔴 Shutting down in {delay} seconds...")
            print("💡 Close all important applications now!")
            
            if self.os_type == 'Windows':
                subprocess.run(['shutdown', '/s', '/t', str(delay)])
                print(f"✅ Shutdown scheduled in {delay} seconds")
                return True
            
            elif self.os_type == 'Darwin':  # macOS
                subprocess.run(['sudo', 'shutdown', '-h', f'+{delay//60}'])
                print(f"✅ Shutdown scheduled in {delay} seconds")
                return True
            
            elif self.os_type == 'Linux':
                subprocess.run(['shutdown', '-h', f'+{delay//60}'])
                print(f"✅ Shutdown scheduled in {delay} seconds")
                return True
            
            else:
                logger.error(f"Shutdown not supported on {self.os_type}")
                print(f"❌ Shutdown not supported on {self.os_type}")
                return False
                
        except Exception as e:
            logger.error(f"Shutdown failed: {e}", exc_info=True)
            print(f"❌ Shutdown failed: {e}")
            return False
    
    def restart(self, delay: int = 60, force: bool = False, gui_mode: bool = True) -> bool:
        """
        Restart the computer
        
        Args:
            delay: Delay in seconds before restart (default: 60)
            force: Force restart without saving (default: False)
            gui_mode: Use GUI dialog instead of terminal input (default: True)
        
        Returns:
            bool: True if restart initiated
        """
        try:
            # Confirm action
            if not force and not self._confirm_action("restart the computer", use_gui=gui_mode):
                logger.info("Restart cancelled by user")
                print("❌ Restart cancelled")
                return False
            
            logger.warning(f"Initiating restart in {delay} seconds")
            print(f"\n🔄 Restarting in {delay} seconds...")
            print("💡 Close all important applications now!")
            
            if self.os_type == 'Windows':
                subprocess.run(['shutdown', '/r', '/t', str(delay)])
                print(f"✅ Restart scheduled in {delay} seconds")
                return True
            
            elif self.os_type == 'Darwin':  # macOS
                subprocess.run(['sudo', 'shutdown', '-r', f'+{delay//60}'])
                print(f"✅ Restart scheduled in {delay} seconds")
                return True
            
            elif self.os_type == 'Linux':
                subprocess.run(['shutdown', '-r', f'+{delay//60}'])
                print(f"✅ Restart scheduled in {delay} seconds")
                return True
            
            else:
                logger.error(f"Restart not supported on {self.os_type}")
                print(f"❌ Restart not supported on {self.os_type}")
                return False
                
        except Exception as e:
            logger.error(f"Restart failed: {e}", exc_info=True)
            print(f"❌ Restart failed: {e}")
            return False
    
    def sleep(self) -> bool:
        """Put the computer to sleep"""
        try:
            logger.info("Putting computer to sleep")
            print("\n😴 Putting computer to sleep...")
            
            if self.os_type == 'Windows':
                # Use rundll32 to sleep
                subprocess.run([
                    'rundll32.exe', 'powrprof.dll,SetSuspendState',
                    '0', '1', '0'
                ])
                print("✅ Computer going to sleep")
                return True
            
            elif self.os_type == 'Darwin':  # macOS
                subprocess.run(['pmset', 'sleepnow'])
                print("✅ Computer going to sleep")
                return True
            
            elif self.os_type == 'Linux':
                subprocess.run(['systemctl', 'suspend'])
                print("✅ Computer going to sleep")
                return True
            
            else:
                logger.error(f"Sleep not supported on {self.os_type}")
                print(f"❌ Sleep not supported on {self.os_type}")
                return False
                
        except Exception as e:
            logger.error(f"Sleep failed: {e}", exc_info=True)
            print(f"❌ Sleep failed: {e}")
            return False
    
    def lock_screen(self) -> bool:
        """Lock the screen"""
        try:
            logger.info("Locking screen")
            print("\n🔒 Locking screen...")
            
            if self.os_type == 'Windows':
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
                print("✅ Screen locked")
                return True
            
            elif self.os_type == 'Darwin':  # macOS
                subprocess.run([
                    '/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession',
                    '-suspend'
                ])
                print("✅ Screen locked")
                return True
            
            elif self.os_type == 'Linux':
                # Try different lock commands
                lock_commands = [
                    ['gnome-screensaver-command', '--lock'],
                    ['xdg-screensaver', 'lock'],
                    ['loginctl', 'lock-session']
                ]
                
                for cmd in lock_commands:
                    try:
                        subprocess.run(cmd, check=True)
                        print("✅ Screen locked")
                        return True
                    except (FileNotFoundError, subprocess.CalledProcessError):
                        continue
                
                logger.error("No lock command available on Linux")
                print("❌ No lock command available")
                return False
            
            else:
                logger.error(f"Lock screen not supported on {self.os_type}")
                print(f"❌ Lock screen not supported on {self.os_type}")
                return False
                
        except Exception as e:
            logger.error(f"Lock screen failed: {e}", exc_info=True)
            print(f"❌ Lock screen failed: {e}")
            return False
    
    # ==================== SYSTEM INFO ====================
    
    def get_system_info(self) -> dict:
        """
        Get system information
        
        Returns:
            dict: System information
        """
        import psutil
        
        info = {
            'os': self.os_type,
            'os_version': platform.version(),
            'hostname': platform.node(),
            'processor': platform.processor(),
            'cpu_count': os.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_total': f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
            'memory_used': f"{psutil.virtual_memory().used / (1024**3):.2f} GB",
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': f"{psutil.disk_usage('/').percent}%"
        }
        
        return info
    
    def show_system_info(self):
        """Display system information"""
        print("\n💻 System Information:")
        print("=" * 50)
        
        info = self.get_system_info()
        
        for key, value in info.items():
            display_key = key.replace('_', ' ').title()
            print(f"  {display_key}: {value}")
        
        print("=" * 50)


# Convenience functions for Intent_OS
def take_screenshot(filename: Optional[str] = None) -> bool:
    """Take a screenshot (convenience function)"""
    sys_cmd = SystemCommands()
    return sys_cmd.take_screenshot(filename)


def adjust_volume(level: int) -> bool:
    """Adjust volume (convenience function)"""
    sys_cmd = SystemCommands()
    return sys_cmd.adjust_volume(level)


def lock_screen() -> bool:
    """Lock screen (convenience function)"""
    sys_cmd = SystemCommands()
    return sys_cmd.lock_screen()


def shutdown_computer(delay: int = 60) -> bool:
    """Shutdown computer (convenience function)"""
    sys_cmd = SystemCommands()
    return sys_cmd.shutdown(delay)


def restart_computer(delay: int = 60) -> bool:
    """Restart computer (convenience function)"""
    sys_cmd = SystemCommands()
    return sys_cmd.restart(delay)


def sleep_computer() -> bool:
    """Sleep computer (convenience function)"""
    sys_cmd = SystemCommands()
    return sys_cmd.sleep()


# Test function
def test_system_commands():
    """Test the System Commands module"""
    print("\n" + "=" * 60)
    print("🧪 Testing System Commands")
    print("=" * 60)
    
    sys_cmd = SystemCommands()
    
    # Test system info
    print("\n1️⃣ Testing system info...")
    sys_cmd.show_system_info()
    
    # Test screenshot
    print("\n2️⃣ Testing screenshot...")
    choice = input("Take a test screenshot? (yes/no): ").strip().lower()
    if choice in ['yes', 'y']:
        sys_cmd.take_screenshot("test_screenshot")
    
    print("\n" + "=" * 60)
    print("✅ System Commands test complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_system_commands()
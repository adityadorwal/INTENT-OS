"""
WhatsApp Bot Bridge
Connects voice command system with WhatsApp automated chatbot
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional
from logger_config import get_logger
import psutil

logger = get_logger(__name__)

class WhatsAppBotBridge:
    """Bridge to control WhatsApp automated chatbot from voice commands"""
    
    def __init__(self):
        """Initialize WhatsApp bot bridge"""
        self.bot_dir = Path(__file__).parent / "Chat_Automation"
        self.bot_process: Optional[subprocess.Popen] = None
        self.pid_file = self.bot_dir / "whatsapp_bot.pid"
        
        logger.info("WhatsApp Bot Bridge initialized")
    
    def is_running(self) -> bool:
        """
        Check if WhatsApp bot is currently running
        
        Returns:
            bool: True if bot is running
        """
        # Check if process object exists and is running
        if self.bot_process and self.bot_process.poll() is None:
            return True
        
        # Check PID file
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                if psutil.pid_exists(pid):
                    try:
                        process = psutil.Process(pid)
                        if process.is_running():
                            logger.info(f"Bot is running (PID: {pid})")
                            return True
                    except psutil.NoSuchProcess:
                        pass
                
                # PID file exists but process doesn't - clean up
                self.pid_file.unlink()
            except Exception as e:
                logger.error(f"Error checking PID file: {e}")
        
        return False
    
    def start_bot(self) -> bool:
        """
        Start WhatsApp automated chatbot
        
        Returns:
            bool: True if bot started successfully
        """
        try:
            # Check if already running
            if self.is_running():
                logger.warning("WhatsApp bot is already running")
                print("⚠️ WhatsApp bot is already running")
                return False
            
            # Locate bot script
            bot_script = self.bot_dir / "whatsapp_automation" / "automated_chatbot.py"
            
            if not bot_script.exists():
                logger.error(f"Bot script not found: {bot_script}")
                print(f"❌ Bot script not found: {bot_script}")
                return False
            
            logger.info("Starting WhatsApp bot...")
            print("\n🤖 Starting WhatsApp Bot...")
            
            # Start bot process
            if os.name == 'nt':  # Windows
                # Use pythonw to run without console window
                pythonw_path = sys.executable.replace('python.exe', 'pythonw.exe')
                if not os.path.exists(pythonw_path):
                    pythonw_path = sys.executable
                
                self.bot_process = subprocess.Popen(
                    [pythonw_path, str(bot_script)],
                    cwd=str(self.bot_dir),
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:  # Linux/Mac
                self.bot_process = subprocess.Popen(
                    [sys.executable, str(bot_script)],
                    cwd=str(self.bot_dir),
                    start_new_session=True
                )
            
            # Save PID
            pid = self.bot_process.pid
            with open(self.pid_file, 'w') as f:
                f.write(str(pid))
            
            logger.info(f"WhatsApp bot started successfully (PID: {pid})")
            print(f"✅ WhatsApp bot started (PID: {pid})")
            print("💡 Bot will open in a new window")
            
            return True
        
        except FileNotFoundError:
            logger.error("Python executable not found")
            print("❌ Python executable not found")
            return False
        
        except Exception as e:
            logger.error(f"Failed to start WhatsApp bot: {e}", exc_info=True)
            print(f"❌ Failed to start WhatsApp bot: {e}")
            return False
    
    def stop_bot(self) -> bool:
        """
        Stop WhatsApp automated chatbot
        
        Returns:
            bool: True if bot stopped successfully
        """
        try:
            # Check if bot is running
            if not self.is_running():
                logger.info("WhatsApp bot is not running")
                print("ℹ️ WhatsApp bot is not running")
                return False
            
            logger.info("Stopping WhatsApp bot...")
            print("\n⏹️ Stopping WhatsApp bot...")
            
            # Try to terminate gracefully first
            if self.bot_process:
                try:
                    self.bot_process.terminate()
                    self.bot_process.wait(timeout=5)
                    logger.info("Bot process terminated")
                except subprocess.TimeoutExpired:
                    logger.warning("Bot didn't terminate gracefully, forcing...")
                    self.bot_process.kill()
                    self.bot_process.wait()
                    logger.info("Bot process killed")
                
                self.bot_process = None
            
            # Also try using PID file
            if self.pid_file.exists():
                try:
                    with open(self.pid_file, 'r') as f:
                        pid = int(f.read().strip())
                    
                    if psutil.pid_exists(pid):
                        process = psutil.Process(pid)
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except psutil.TimeoutExpired:
                            process.kill()
                    
                    self.pid_file.unlink()
                except Exception as e:
                    logger.error(f"Error stopping via PID: {e}")
            
            print("✅ WhatsApp bot stopped")
            logger.info("WhatsApp bot stopped successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to stop WhatsApp bot: {e}", exc_info=True)
            print(f"❌ Failed to stop bot: {e}")
            return False
    
    def restart_bot(self) -> bool:
        """
        Restart WhatsApp bot
        
        Returns:
            bool: True if restarted successfully
        """
        logger.info("Restarting WhatsApp bot...")
        print("\n🔄 Restarting WhatsApp bot...")
        
        # Stop if running
        if self.is_running():
            if not self.stop_bot():
                return False
            
            # Wait a moment
            import time
            time.sleep(2)
        
        # Start
        return self.start_bot()
    
    def get_status(self) -> dict:
        """
        Get current bot status
        
        Returns:
            dict: Status information
        """
        is_running = self.is_running()
        
        status = {
            'running': is_running,
            'status_text': '🟢 Running' if is_running else '🔴 Stopped'
        }
        
        if is_running and self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    status['pid'] = int(f.read().strip())
            except:
                pass
        
        return status
    
    def cleanup(self):
        """Cleanup bot on application exit"""
        logger.info("Cleaning up WhatsApp bot...")
        
        if self.is_running():
            self.stop_bot()
        
        # Remove PID file if exists
        if self.pid_file.exists():
            try:
                self.pid_file.unlink()
                logger.info("PID file removed")
            except Exception as e:
                logger.error(f"Error removing PID file: {e}")


# Convenience functions for easy import
_bot_instance: Optional[WhatsAppBotBridge] = None

def get_whatsapp_bot() -> WhatsAppBotBridge:
    """Get singleton instance of WhatsApp bot bridge"""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = WhatsAppBotBridge()
    return _bot_instance

def start_whatsapp_bot() -> bool:
    """Start WhatsApp bot (convenience function)"""
    return get_whatsapp_bot().start_bot()

def stop_whatsapp_bot() -> bool:
    """Stop WhatsApp bot (convenience function)"""
    return get_whatsapp_bot().stop_bot()

def is_whatsapp_bot_running() -> bool:
    """Check if bot is running (convenience function)"""
    return get_whatsapp_bot().is_running()

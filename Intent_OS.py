#!/usr/bin/env python3
"""
INTENT_OS - Main Controller
The brain of your AI-powered OS automation system

This controller:
1. Takes user commands (voice/text)
2. Uses Intent Classifier to understand what user wants
3. Routes to appropriate action handlers
4. Executes the requested operations
5. Integrates with Observer productivity tracker
6. PROTECTED by 4-tier security system (Phase 2)
"""

import sys
import os
import json
import time
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional

# Import file operations bridge
from file_operations_bridge import FileOperationsBridge

# Import security manager (Phase 2)
from security_manager import get_security_manager

# Import logging
from logger_config import get_intent_os_logger, log_error

# Initialize logger
logger = get_intent_os_logger()


class IntentOS:
    """
    Main Intent_OS Controller
    
    The central brain that orchestrates all user commands
    and routes them to appropriate handlers
    """
    
    def __init__(self):
        """Initialize Intent_OS with all components"""
        logger.info("Initializing Intent_OS...")
        print("🚀 Initializing Intent_OS...")
        
        # Security manager (Phase 2)
        try:
            self.security = get_security_manager()
            logger.info("Security manager initialized successfully")
            print("🔐 Security system ready!")
        except Exception as e:
            logger.error(f"Security manager initialization failed: {e}", exc_info=True)
            print(f"⚠️  Security manager initialization failed: {e}")
            self.security = None
        
        # Observer integration
        self.observer_server_running = False
        self.observer_tracker_running = False
        
        # File operations integration
        try:
            self.file_ops = FileOperationsBridge()
            logger.info("File operations bridge initialized successfully")
            print("📁 File operations ready!")
        except Exception as e:
            logger.error(f"File operations initialization failed: {e}", exc_info=True)
            log_error(f"File operations initialization failed: {e}")
            print(f"⚠️  File operations initialization failed: {e}")
            self.file_ops = None
        
        # Note: Intent_classifier will be set by main.py to avoid circular imports
        self.classifier = None
        
        logger.info("Intent_OS initialization complete")
        print("🧠 Intent_OS ready to serve!")
        print("📝 Commands can be sent via voice or text")
        print("🎯 Type 'help' for available commands")
        print("🛑 Type 'exit' to quit")
    
    def _check_security_authorization(self, action: str, description: Optional[str] = None) -> bool:
        """
        Check if action is authorized by security system
        
        Args:
            action: Action to authorize
            description: Human-readable description
            
        Returns:
            True if authorized, False otherwise
        """
        if not self.security:
            # Security not available, allow action
            logger.warning(f"Security manager not available, allowing '{action}'")
            return True
        
        try:
            authorized = self.security.authorize_action(action, description, parent=None)
            
            if not authorized:
                logger.info(f"Action '{action}' denied by security system")
                print(f"\n🔒 Action denied by security system")
                print(f"💡 You cancelled or failed security verification")
                
                # Show notification
                try:
                    from notifications import get_notification_manager
                    notification_manager = get_notification_manager()
                    notification_manager.warning(
                        "Action Blocked",
                        f"{description or action} was blocked by security",
                        duration=4
                    )
                except:
                    pass
            
            return authorized
            
        except Exception as e:
            logger.error(f"Security check failed for '{action}': {e}", exc_info=True)
            print(f"⚠️  Security check error: {e}")
            # On error, deny for safety
            return False
    
    def start_command_loop(self):
        """Main command processing loop"""
        print("\n" + "="*60)
        print("🎯 INTENT_OS COMMAND INTERFACE")
        print("="*60)
        
        while True:
            try:
                # Get user input
                command = input("\n📝 Your command: ").strip()
                
                if not command:
                    continue
                
                # Handle system commands
                if command.lower() in ['exit', 'quit', 'stop']:
                    print("🛑 Shutting down Intent_OS...")
                    break
                
                elif command.lower() == 'help':
                    self._show_help()
                    continue
                
                elif command.lower() == 'status':
                    self._show_system_status()
                    continue
                
                # Process user command through intent classifier
                self._process_command(command)
                
            except KeyboardInterrupt:
                print("\n🛑 Interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error processing command: {e}")
    
    def _process_command(self, command: str):
        """Process command through intent classification"""
        try:
            logger.info(f"Processing command: {command}")
            
            # Classify the intent
            intent = self.classifier.classify(command)
            
            logger.info(f"Intent classified - Category: {intent.category}, Action: {intent.action}")
            logger.debug(f"Intent parameters: {intent.parameters}")
            
            print(f"\n🧠 Classified: {intent}")
            print(f"🎯 Action Path: {self.classifier.get_action_path(intent)}")
            
            # Route to appropriate handler
            self._route_to_handler(intent)
            
        except Exception as e:
            logger.error(f"Command processing failed: {e}", exc_info=True)
            log_error(f"Command processing error for '{command}': {e}")
            print(f"❌ Command processing failed: {e}")
    
    def _route_to_handler(self, intent: Any):
        """Route intent to appropriate handler"""
        category = intent.category
        action = intent.action
        params = intent.parameters
        
        # Observer commands
        if category == "observer":
            self._handle_observer_commands(action, params)
        
        # Messaging commands
        elif category == "messaging":
            self._handle_messaging_commands(action, params)
        
        # Web commands
        elif category == "web":
            self._handle_web_commands(action, params)
        
        # File operations
        elif category == "file_ops":
            self._handle_file_commands(action, params)
        
        # App control
        elif category == "app_control":
            self._handle_app_commands(action, params)
        
        # System commands
        elif category == "system":
            self._handle_system_commands(action, params)
        
        # Download commands
        elif category == "download":
            self._handle_download_commands(action, params)
        
        # Automation commands
        elif category == "automation":
            self._handle_automation_commands(action, params)
        
        # Form Filler commands
        elif category == "form_filler":
            self._handle_form_filler_commands(action, params)
        
        # WhatsApp Bot commands (NEW)
        elif category == "whatsapp_bot":
            self._handle_whatsapp_bot_commands(action, params)
        
        # Conversation commands (NEW)
        elif category == "conversation":
            self._handle_conversation_commands(action, params)
        
        # Unknown/general
        else:
            print(f"❓ Unknown category: {category}")
            
            # Try conversation for general category
            if category == "general":
                params["question"] = params.get("raw", "unknown command")
                self._handle_conversation_commands("general_question", params)
            else:
                raw_command = params.get('raw', 'unknown command')
                print(f"💡 Suggestion: Check if '{raw_command}' is supported")
    
    def _handle_observer_commands(self, action: str, params: Dict[str, Any]):
        """Handle Observer productivity tracker commands"""
        print(f"📊 Observer Command: {action}")
        
        if action == "show_status":
            self._show_observer_status()
        
        elif action == "show_productivity":
            self._show_productivity_dashboard()
        
        elif action == "open_dashboard":
            self._show_productivity_dashboard()
        
        elif action == "start_tracking":
            print("❌ SECURITY: Tracking can only be controlled via mouse toggle button")
            print("💡 Use the Observer ON/OFF button in the main interface")
        
        elif action == "stop_tracking":
            print("❌ SECURITY: Tracking can only be controlled via mouse toggle button")
            print("💡 Use the Observer ON/OFF button in the main interface")
        
        else:
            print(f"❓ Unknown Observer action: {action}")
            print("💡 Available: status, productivity, dashboard")
    
    def _show_observer_status(self):
        """Show Observer system status"""
        print("📊 Observer Status:")
        print(f"🖥  Server running: {'✅' if self.observer_server_running else '❌'}")
        print(f"📈  Tracker running: {'✅' if self.observer_tracker_running else '❌'}")
        
        # Check if Observer files exist
        observer_dir = Path("Observer")
        if observer_dir.exists():
            print("📁 Observer directory: ✅ Found")
            db_path = observer_dir / "productivity_data.db"
            if db_path.exists():
                print("💾 Database: ✅ Found")
            else:
                print("💾 Database: ❌ Not found (run setup)")
        else:
            print("📁 Observer directory: ❌ Not found")
    
    def _show_productivity_dashboard(self):
        """Show productivity dashboard"""
        print("🚀 Opening productivity dashboard...")
        
        try:
            # Start Observer server if not running
            if not self.observer_server_running:
                self._start_observer_server()
                time.sleep(2)  # Give server time to start
            
            # Open dashboard in browser
            webbrowser.open("http://localhost:8000/dashboard.html")
            print("✅ Dashboard opened in browser")
            
        except Exception as e:
            print(f"❌ Failed to open dashboard: {e}")
    
    def _open_observer_dashboard(self):
        """Open Observer dashboard"""
        self._show_productivity_dashboard()
    
    def _start_observer_tracking(self):
        """Start Observer tracking"""
        print("📈 Starting Observer tracking...")
        
        try:
            if not self.observer_tracker_running:
                # Navigate to Observer directory and start tracker
                observer_script = Path("Observer") / "tracker.py"
                if observer_script.exists():
                    subprocess.Popen(["python", str(observer_script)], cwd="Observer")
                    self.observer_tracker_running = True
                    print("✅ Observer tracking started")
                else:
                    print("❌ Observer tracker.py not found")
            else:
                print("ℹ️ Observer tracking already running")
                
        except Exception as e:
            print(f"❌ Failed to start tracking: {e}")
    
    def _stop_observer_tracking(self):
        """Stop Observer tracking"""
        print("🛑 Stopping Observer tracking...")
        self.observer_tracker_running = False
        print("✅ Observer tracking stopped")
    
    def _start_observer_server(self):
        """Start Observer dashboard server"""
        print("🌐 Starting Observer server...")
        
        try:
            # Get absolute path to avoid double Observer issue
            observer_dir = Path(__file__).parent / "Observer"
            server_script = observer_dir / "server.py"
            
            if server_script.exists():
                subprocess.Popen(
                    [sys.executable, str(server_script)],
                    cwd=str(observer_dir)
                )
                self.observer_server_running = True
                print("✅ Observer server started")
            else:
                print(f"❌ Observer server.py not found at: {server_script}")
                
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
    
    def _handle_messaging_commands(self, action: str, params: Dict[str, Any]):
        """Handle messaging commands"""
        print(f"💬 Messaging: {action}")
        
        if action == "send_message":
            recipient = params.get("recipient", "unknown")
            message = params.get("message", "")
            
            # Validate inputs
            if recipient == "unknown" or not recipient:
                print("❌ No recipient specified!")
                return
            
            if not message:
                print("❌ No message content!")
                return
            
            print(f"\n📤 Sending WhatsApp message:")
            print(f"   To: {recipient}")
            print(f"   Message: {message}")
            
            # Import and use WhatsApp bridge
            try:
                from whatsapp_bridge import send_whatsapp_message
                
                success = send_whatsapp_message(recipient, message)
                
                if success:
                    print("✅ Message sent successfully!")
                else:
                    print("❌ Failed to send message")
                    print("💡 Make sure WhatsApp Web is logged in")
                    
            except ImportError:
                print("❌ WhatsApp bridge not available!")
                print("💡 Make sure whatsapp_bridge.py exists in the project folder")
                
            except Exception as e:
                print(f"❌ Error sending message: {e}")
        
        elif action == "open_chat":
            recipient = params.get("recipient", "unknown")
            print(f"💬 Would open chat with: {recipient}")
            print("💡 This feature will be added in the next update!")
        
        else:
            print(f"❓ Unknown messaging action: {action}")
    
    def _handle_web_commands(self, action: str, params: Dict[str, Any]):
        """Handle web commands"""
        print(f"🌐 Web: {action}")
        
        if action == "search":
            query = params.get("query", "")
            if not query:
                print("❌ No search query provided!")
                return
            
            print(f"🔍 Searching for: '{query}'")
            try:
                import webbrowser
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                webbrowser.open(search_url)
                print(f"✅ Opened Google search for: {query}")
            except Exception as e:
                print(f"❌ Error opening search: {e}")
        
        elif action == "play_youtube":
            query = params.get("query", "")
            platform = params.get("platform", "youtube")
            
            if not query:
                print("❌ No video query provided!")
                return
            
            print(f"🎵 Playing on {platform}: '{query}'")
            try:
                import webbrowser
                if platform == "youtube":
                    youtube_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                    webbrowser.open(youtube_url)
                    print(f"✅ Opened YouTube search for: {query}")
                elif platform == "spotify":
                    spotify_url = f"https://open.spotify.com/search/{query.replace(' ', '%20')}"
                    webbrowser.open(spotify_url)
                    print(f"✅ Opened Spotify search for: {query}")
                else:
                    print(f"❓ Unknown platform: {platform}")
            except Exception as e:
                print(f"❌ Error opening {platform}: {e}")
        
        elif action == "open_website":
            url = params.get("url", "")
            if not url:
                print("❌ No URL provided!")
                return
            
            print(f"🌐 Opening website: {url}")
            try:
                import webbrowser
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                webbrowser.open(url)
                print(f"✅ Opened: {url}")
            except Exception as e:
                print(f"❌ Error opening website: {e}")
        
        else:
            print(f"❓ Unknown web action: {action}")
    
    def _handle_file_commands(self, action: str, params: Dict[str, Any]):
        """Handle file operation commands"""
        print(f"📁 File Operation: {action}")
        
        if not self.file_ops:
            print("❌ File operations not available")
            return
        
        if action == "organize_files":
            folder = params.get("folder", "downloads")
            print(f"📂 Organizing folder: '{folder}'")
            success = self.file_ops.organize_folder(folder)
            if success:
                print("✅ Folder organized successfully!")
            else:
                print("❌ Failed to organize folder")
        
        elif action == "compress_folder":
            folder = params.get("folder", "")
            output = params.get("output_name", None)
            
            if not folder:
                print("❌ No folder specified for compression")
                print("💡 Example: 'compress my documents folder'")
                return
            
            print(f"🗜️  Compressing: '{folder}'")
            success = self.file_ops.compress_folder(folder, output)
            if success:
                print("✅ Compression complete!")
            else:
                print("❌ Compression failed")
        
        elif action == "extract_archive":
            archive = params.get("archive", "")
            destination = params.get("destination", None)
            
            if not archive:
                print("❌ No archive specified for extraction")
                print("💡 Example: 'extract backup.zip'")
                return
            
            print(f"📦 Extracting: '{archive}'")
            success = self.file_ops.extract_archive(archive, destination)
            if success:
                print("✅ Extraction complete!")
            else:
                print("❌ Extraction failed")
        
        elif action == "delete_files":
            file_path = params.get("file", "")
            
            if not file_path:
                print("❌ No file specified for deletion")
                return
            
            # Security check (Tier 3: PIN required)
            if not self._check_security_authorization("delete_files", f"Delete '{file_path}'"):
                return
            
            print(f"🗑️  Delete request for: '{file_path}'")
            success = self.file_ops.delete_file(file_path, confirm=True)
            if success:
                print("✅ File deleted successfully!")
            else:
                print("❌ Deletion cancelled or failed")
        
        else:
            print(f"❓ Unknown file action: {action}")
            print("💡 Available: organize_files, compress_folder, extract_archive, delete_files")
    
    def _handle_app_commands(self, action: str, params: Dict[str, Any]):
        """Handle app control commands"""
        print(f"🖥 Apps: {action}")
        app_name = params.get("app_name", "")
        
        if not app_name:
            print("❌ No app name provided!")
            return
        
        if action == "open_app":
            print(f"🚀 Opening app: '{app_name}'")
            try:
                import subprocess
                import platform
                
                system = platform.system()
                
                # Common app mappings
                app_mappings = {
                    'chrome': 'google-chrome' if system == 'Linux' else 'chrome',
                    'firefox': 'firefox',
                    'edge': 'msedge' if system == 'Windows' else 'microsoft-edge',
                    'notepad': 'notepad',
                    'calculator': 'calc' if system == 'Windows' else 'gnome-calculator',
                    'file explorer': 'explorer' if system == 'Windows' else 'nautilus',
                    'terminal': 'cmd' if system == 'Windows' else 'gnome-terminal',
                }
                
                # Get the actual command
                app_command = app_mappings.get(app_name.lower(), app_name)
                
                if system == 'Windows':
                    subprocess.Popen(['start', app_command], shell=True)
                elif system == 'Darwin':  # macOS
                    subprocess.Popen(['open', '-a', app_name])
                else:  # Linux
                    subprocess.Popen([app_command])
                
                print(f"✅ Launched: {app_name}")
                
            except Exception as e:
                print(f"❌ Error opening app: {e}")
                print(f"💡 Try using the full app name or path")
        
        elif action == "close_app":
            # Security check (Tier 3: PIN required)
            if not self._check_security_authorization("close_app", f"Close '{app_name}'"):
                return
            
            print(f"🛑 Closing app: '{app_name}'")
            try:
                import psutil
                import platform
                
                # Try to find and kill the process
                killed = False
                for proc in psutil.process_iter(['name']):
                    if app_name.lower() in proc.info['name'].lower():
                        proc.terminate()
                        killed = True
                        print(f"✅ Closed: {proc.info['name']}")
                
                if not killed:
                    print(f"⚠️  Process '{app_name}' not found")
                    print(f"💡 Make sure the app is running")
                    
            except Exception as e:
                print(f"❌ Error closing app: {e}")
        
        else:
            print(f"❓ Unknown app action: {action}")
    
    def _handle_system_commands(self, action: str, params: Dict[str, Any]):
        """Handle system commands"""
        logger.info(f"System command: {action}")
        print(f"⚙️  System: {action}")
        
        try:
            # Import system commands module
            from system_commands import SystemCommands
            sys_cmd = SystemCommands()
            
            if action == "screenshot":
                filename = params.get("filename")
                success = sys_cmd.take_screenshot(filename)
                if success:
                    logger.info("Screenshot taken successfully")
                else:
                    logger.warning("Screenshot failed")
            
            elif action == "volume_control":
                level = params.get("level", 50)
                success = sys_cmd.adjust_volume(level)
                if success:
                    logger.info(f"Volume adjusted to {level}%")
                else:
                    logger.warning("Volume adjustment failed")
            
            elif action == "lock":
                success = sys_cmd.lock_screen()
                if success:
                    logger.info("Screen locked")
                else:
                    logger.warning("Lock screen failed")
            
            elif action == "shutdown":
                # Security check (Tier 4: PIN + Critical warning)
                if not self._check_security_authorization("shutdown", "Shutdown Computer"):
                    return
                
                delay = params.get("delay", 60)
                success = sys_cmd.shutdown(delay=delay)
                if success:
                    logger.warning(f"Shutdown initiated with {delay}s delay")
                else:
                    logger.warning("Shutdown failed")
            
            elif action == "restart":
                # Security check (Tier 4: PIN + Critical warning)
                if not self._check_security_authorization("restart", "Restart Computer"):
                    return
                
                delay = params.get("delay", 60)
                success = sys_cmd.restart(delay=delay)
                if success:
                    logger.warning(f"Restart initiated with {delay}s delay")
                else:
                    logger.warning("Restart failed")
            
            elif action == "sleep":
                # Security check (Tier 4: PIN + Critical warning)
                if not self._check_security_authorization("sleep", "Put Computer to Sleep"):
                    return
                
                success = sys_cmd.sleep()
                if success:
                    logger.info("Computer going to sleep")
                else:
                    logger.warning("Sleep failed")
            
            elif action == "clean_temp":
                print("💡 Temp file cleaning coming soon!")
                logger.info("Temp clean requested (not implemented)")
            
            else:
                print(f"❓ Unknown system action: {action}")
                logger.warning(f"Unknown system action: {action}")
        
        except ImportError as e:
            logger.error(f"System commands module not available: {e}")
            print("❌ System commands module not available!")
            print("💡 Make sure system_commands.py exists")
        except Exception as e:
            logger.error(f"System command failed: {e}", exc_info=True)
            log_error(f"System command error ({action}): {e}")
            print(f"❌ System command failed: {e}")
    
    def _handle_form_filler_commands(self, action: str, params: Dict[str, Any]):
        """Handle form filler commands"""
        logger.info(f"Form filler command: {action}")
        print(f"🤖 Form Filler: {action}")
        
        try:
            # Import form filler bridge
            from form_filler_bridge import FormFillerBridge
            bridge = FormFillerBridge()
            
            if action == "start_form_filler":
                success = bridge.start_form_filler()
                if success:
                    logger.info("Form filler started")
                else:
                    logger.warning("Form filler start failed")
            
            elif action == "stop_form_filler":
                bridge.stop_form_filler()
                logger.info("Form filler stop requested")
            
            elif action == "update_form_data":
                # Interactive update
                success = bridge.interactive_update()
                if success:
                    logger.info("Form data updated")
                else:
                    logger.info("Form data update cancelled or failed")
            
            elif action == "show_form_data":
                bridge.show_user_data()
                logger.info("Form data displayed")
            
            else:
                print(f"❓ Unknown form filler action: {action}")
                logger.warning(f"Unknown form filler action: {action}")
        
        except ImportError as e:
            logger.error(f"Form filler bridge not available: {e}")
            print("❌ Form filler bridge not available!")
            print("💡 Make sure form_filler_bridge.py exists")
        except Exception as e:
            logger.error(f"Form filler command failed: {e}", exc_info=True)
            log_error(f"Form filler error ({action}): {e}")
            print(f"❌ Form filler command failed: {e}")
    
    def _handle_whatsapp_bot_commands(self, action: str, params: Dict[str, Any]):
        """Handle WhatsApp bot control commands"""
        logger.info(f"WhatsApp bot command: {action}")
        print(f"🤖 WhatsApp Bot: {action}")
        
        try:
            # Import WhatsApp bot bridge
            from whatsapp_bot_bridge import WhatsAppBotBridge
            bot = WhatsAppBotBridge()
            
            if action == "start_bot":
                success = bot.start_bot()
                if success:
                    logger.info("WhatsApp bot started successfully")
                    print("✅ WhatsApp bot started!")
                    print("💡 Bot window should open shortly")
                    
                    # Notification
                    try:
                        from notifications import get_notification_manager
                        notification_manager = get_notification_manager()
                        notification_manager.success(
                            "WhatsApp Bot",
                            "Automated chatbot started successfully!",
                            duration=4
                        )
                    except:
                        pass
                else:
                    logger.warning("WhatsApp bot start failed")
                    print("⚠️ Failed to start WhatsApp bot")
            
            elif action == "stop_bot":
                success = bot.stop_bot()
                if success:
                    logger.info("WhatsApp bot stopped successfully")
                    print("✅ WhatsApp bot stopped")
                    
                    # Notification
                    try:
                        from notifications import get_notification_manager
                        notification_manager = get_notification_manager()
                        notification_manager.info(
                            "WhatsApp Bot",
                            "Automated chatbot stopped",
                            duration=3
                        )
                    except:
                        pass
                else:
                    logger.info("WhatsApp bot was not running")
            
            elif action == "restart_bot":
                success = bot.restart_bot()
                if success:
                    logger.info("WhatsApp bot restarted successfully")
                    print("✅ WhatsApp bot restarted")
                    
                    # Notification
                    try:
                        from notifications import get_notification_manager
                        notification_manager = get_notification_manager()
                        notification_manager.success(
                            "WhatsApp Bot",
                            "Automated chatbot restarted!",
                            duration=3
                        )
                    except:
                        pass
                else:
                    logger.warning("WhatsApp bot restart failed")
                    print("⚠️ Failed to restart WhatsApp bot")
            
            elif action == "bot_status":
                status = bot.get_status()
                logger.info(f"WhatsApp bot status: {status}")
                print(f"\n📊 WhatsApp Bot Status:")
                print(f"   Status: {status['status_text']}")
                if 'pid' in status:
                    print(f"   PID: {status['pid']}")
                print()
                
                # Notification
                try:
                    from notifications import get_notification_manager
                    notification_manager = get_notification_manager()
                    notification_manager.info(
                        "WhatsApp Bot",
                        status['status_text'],
                        duration=3
                    )
                except:
                    pass
            
            else:
                print(f"❓ Unknown WhatsApp bot action: {action}")
                logger.warning(f"Unknown WhatsApp bot action: {action}")
                print("💡 Available: start_bot, stop_bot, restart_bot, bot_status")
        
        except ImportError as e:
            logger.error(f"WhatsApp bot bridge not available: {e}")
            print("❌ WhatsApp bot bridge not available!")
            print("💡 Make sure whatsapp_bot_bridge.py exists")
        except Exception as e:
            logger.error(f"WhatsApp bot command failed: {e}", exc_info=True)
            log_error(f"WhatsApp bot error ({action}): {e}")
            print(f"❌ WhatsApp bot command failed: {e}")
    
    def _handle_download_commands(self, action: str, params: Dict[str, Any]):
        """Handle download commands"""
        print(f"⬇️  Downloads: {action}")
        print("💡 Download integration coming soon!")
    
    def _handle_automation_commands(self, action: str, params: Dict[str, Any]):
        """Handle automation commands"""
        print(f"⏰ Automation: {action}")
        print("💡 Automation integration coming soon!")
    
    def _handle_conversation_commands(self, action: str, params: Dict[str, Any]):
        """Handle general conversation using AI + TTS"""
        print(f"💬 Conversation: {action}")
        
        question = params.get("question", params.get("raw", ""))
        
        try:
            # Import AI handler
            from api_handler import APIHandler
            ai = APIHandler()
            
            # Create conversational prompt
            prompt = f"""You are a helpful voice assistant. Respond to this in 1-2 SHORT sentences:

User: {question}

Guidelines:
- Be friendly and conversational
- Keep response VERY SHORT (1-2 sentences max, under 30 words)
- Don't use lists, bullet points, or formatting
- Sound natural when spoken aloud
- Address user respectfully

Examples:
"are you listening?" → "Yes, I'm listening and ready to help you."
"what can you do?" → "I can send messages, control apps, organize files, take screenshots, track productivity, and much more."
"hello" → "Hello! How may I assist you today?"
"who are you?" → "I'm your voice assistant, here to help with your computer tasks."

Response (1-2 sentences only):"""
            
            # Get AI response
            response = ai.send_request(prompt)
            
            # Clean response
            if isinstance(response, dict):
                response = response.get('response', str(response))
            response = str(response).strip()
            
            # Remove formatting
            response = response.replace('*', '').replace('#', '').replace('-', '')
            
            # Limit to first 2 sentences
            sentences = response.split('.')
            if len(sentences) > 2:
                response = '. '.join(sentences[:2]) + '.'
            
            print(f"\n🤖 Response: {response}\n")
            
            # Speak the response using TTS
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.say(response)
                engine.runAndWait()
                print("✅ Response spoken")
            except Exception as e:
                print(f"⚠️ TTS unavailable: {e}")
                print(f"📝 Response (text): {response}")
            
            # Show notification
            from notifications import get_notification_manager
            notification_manager = get_notification_manager()
            notification_manager.info(
                "Assistant",
                response[:100],
                duration=5
            )
            
        except Exception as e:
            print(f"❌ Conversation handler failed: {e}")
            
            # Fallback
            default_response = "I'm here and listening. How can I help you?"
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(default_response)
                engine.runAndWait()
            except:
                print(f"📝 {default_response}")
    
    def _show_system_status(self):
        """Show overall system status"""
        print("🔧 Intent_OS System Status:")
        print("🧠 Intent Classifier: ✅ Ready")
        print("📊 Observer Integration: ✅ Ready")
        print("💬 Messaging: 🔄 In Development")
        print("🌐 Web Operations: 🔄 In Development")
        print("📁 File Operations: 🔄 In Development")
        print("🖥 App Control: 🔄 In Development")
        print("⚙️ System Operations: 🔄 In Development")
        print("⬇️ Downloads: 🔄 In Development")
        print("⏰ Automation: 🔄 In Development")
    
    def _show_help(self):
        """Show available commands"""
        print("\n" + "="*60)
        print("🎯 INTENT_OS - AVAILABLE COMMANDS")
        print("="*60)
        
        print("\n📊 OBSERVER COMMANDS:")
        print("  • show my productivity status - Show productivity dashboard")
        print("  • open observation dashboard - Open Observer web interface")
        print("  • check observer status - Show Observer system status")
        print("  ❌ start tracking my activities - DISABLED (use mouse toggle)")
        print("  ❌ stop tracking - DISABLED (use mouse toggle)")
        print("    🔒 SECURITY: Tracking controlled only via physical button")
        
        print("\n💬 MESSAGING COMMANDS:")
        print("  • send message to [person] as [message] - Send message")
        
        print("\n🌐 WEB COMMANDS:")
        print("  • search for [query] - Web search")
        print("  • play [song] on youtube - Play YouTube video")
        
        print("\n📁 FILE COMMANDS:")
        print("  • organize my [folder] - Organize files")
        
        print("\n🖥 APP COMMANDS:")
        print("  • open [app name] - Launch application")
        print("  • close [app name] - Close application")
        
        print("\n⚙️ SYSTEM COMMANDS:")
        print("  • screenshot - Take screenshot")
        
        print("\n🔧 SYSTEM:")
        print("  • help - Show this help")
        print("  • status - Show system status")
        print("  • exit - Quit Intent_OS")
        
        print("\n" + "="*60)
        print("💡 Tip: Commands work with voice input too!")
        print("🎯 Just speak naturally and Intent_OS will understand!")


def main():
    """Main entry point"""
    try:
        # Initialize Intent_OS
        intent_os = IntentOS()
        
        # Start command loop
        intent_os.start_command_loop()
        
    except KeyboardInterrupt:
        print("\n🛑 Intent_OS stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        print("\n👋 Thank you for using Intent_OS!")


if __name__ == "__main__":
    main()
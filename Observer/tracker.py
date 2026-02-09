#!/usr/bin/env python3
"""
Productivity Tracker - Window Activity Monitor
Tracks active windows and application usage locally
"""

import time
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import platform
import os

# File locking imports (cross-platform)
try:
    import fcntl  # Linux/Mac
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

try:
    import msvcrt  # Windows
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False

from ai_categorizer import AICategorizer

# Platform-specific imports
system = platform.system()

if system == "Windows":
    import win32gui
    import win32process
    import psutil
elif system == "Darwin":  # macOS
    from AppKit import NSWorkspace
elif system == "Linux":
    try:
        import gi
        gi.require_version('Wnck', '3.0')
        from gi.repository import Wnck
    except:
        print("For Linux, install: sudo apt-get install gir1.2-wnck-3.0")
        exit(1)


class WindowTracker:
    def __init__(self, config_path="config.json"):
        # Ensure we're using the Observer config, not the main config
        current_dir = Path(__file__).parent
        config_path = current_dir / config_path
        
        self.config = self.load_config(str(config_path))
        db_filename = self.config.get("database_path", "productivity_data.db")
        self.db_path = str(current_dir / db_filename)
        # PID file for process management
        self.pid_file = current_dir / "tracker.pid"
        
        # Graceful shutdown flag
        self.shutdown_requested = False
        
        # Register signal handlers for clean shutdown
        import signal
        signal.signal(signal.SIGINT, self._handle_shutdown_signal)
        signal.signal(signal.SIGTERM, self._handle_shutdown_signal)
        
        self.tracking_enabled = False
        self.current_window = None
        self.last_check_time = None
        self.setup_database()
        
        # Initialize AI categorizer
        try:
            self.ai_categorizer = AICategorizer()
            self.ai_enabled = True
            print("✅ AI categorizer initialized")
        except Exception as e:
            print(f"⚠️  AI categorizer disabled: {e}")
            self.ai_categorizer = None
            self.ai_enabled = False
    
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Create default config
            default_config = {
                "database_path": "productivity_data.db",
                "check_interval_seconds": 2,
                "ai_config": {
                    "enabled": False,
                    "api_endpoint": "",
                    "api_key": ""
                },
                "categories": {
                    "productive": ["vscode", "pycharm", "terminal", "cmd", "sublime"],
                    "communication": ["slack", "teams", "discord", "whatsapp"],
                    "browsing": ["chrome", "firefox", "safari", "edge"],
                    "entertainment": ["youtube", "netflix", "spotify", "games"]
                }
            }
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def setup_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS window_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                window_title TEXT,
                app_name TEXT,
                app_path TEXT,
                duration_seconds REAL,
                category TEXT,
                is_productive BOOLEAN
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                total_time_seconds REAL,
                productive_time_seconds REAL,
                productivity_score REAL,
                top_apps TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracking_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME,
                end_time DATETIME,
                total_entries INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
        print(f"✓ Database initialized at: {self.db_path}")
    
    def get_active_window_info(self):
        """Get currently active window information (cross-platform)"""
        try:
            if system == "Windows":
                return self._get_windows_window()
            elif system == "Darwin":
                return self._get_macos_window()
            elif system == "Linux":
                return self._get_linux_window()
        except Exception as e:
            print(f"Error getting window info: {e}")
            return None
    
    def _get_windows_window(self):
        """Get active window on Windows"""
        try:
            window = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(window)
            _, pid = win32process.GetWindowThreadProcessId(window)
            
            try:
                process = psutil.Process(pid)
                app_name = process.name()
                app_path = process.exe()
            except:
                app_name = "Unknown"
                app_path = ""
            
            return {
                "title": window_title,
                "app_name": app_name,
                "app_path": app_path
            }
        except:
            return None
    
    def _get_macos_window(self):
        """Get active window on macOS"""
        try:
            active_app = NSWorkspace.sharedWorkspace().activeApplication()
            app_name = active_app['NSApplicationName']
            app_path = active_app['NSApplicationPath']
            
            # Note: Getting window title on macOS requires accessibility permissions
            # For now, we'll use app name as title
            return {
                "title": app_name,
                "app_name": app_name,
                "app_path": app_path
            }
        except:
            return None
    
    def _get_linux_window(self):
        """Get active window on Linux (using Wnck)"""
        try:
            screen = Wnck.Screen.get_default()
            screen.force_update()
            window = screen.get_active_window()
            
            if window:
                return {
                    "title": window.get_name(),
                    "app_name": window.get_application().get_name(),
                    "app_path": ""
                }
        except:
            return None
    
    def categorize_activity(self, app_name, window_title=""):
        """Categorize the activity based on app name and window title"""
        app_lower = app_name.lower()
        
        # First check traditional categories
        categories = self.config.get("categories", {})
        
        for category, apps in categories.items():
            if any(app.lower() in app_lower for app in apps):
                is_productive = self._is_productive_category(category)
                return category, is_productive
        
        # If not found in traditional categories, use AI
        if self.ai_enabled and self.ai_categorizer:
            try:
                ai_category = self.ai_categorizer.get_ai_category(app_name, window_title)
                is_productive = self._is_productive_category(ai_category)
                print(f"🤖 AI categorized: {app_name} → {ai_category}")
                return ai_category, is_productive
            except Exception as e:
                print(f"⚠️  AI categorization failed: {e}")
        
        # Fallback to uncategorized
        return "others", False
    
    def _is_productive_category(self, category):
        """Check if a category is considered productive"""
        productive_categories = self.config.get("productivity_rules", {}).get("productive_categories", ["productive"])
        return category in productive_categories
    
    def _handle_shutdown_signal(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n⚠️  Received shutdown signal ({signum})")
        self.shutdown_requested = True
        self.tracking_enabled = False
        
    def sanitize_window_title(self, title):
        """Remove potentially sensitive information from window titles"""
        if not title:
            return "Unknown"
        
        # List of sensitive keywords to redact
        sensitive_keywords = [
            'password', 'login', 'sign in', 'bank', 'credit card', 
            'social security', 'ssn', 'medical', 'health', 'patient',
            'private', 'confidential', 'secret', 'paypal', 'venmo',
            'account', 'payment', 'billing', 'invoice'
        ]
        
        title_lower = title.lower()
        
        # Check for sensitive content
        for keyword in sensitive_keywords:
            if keyword in title_lower:
                # Return generic description instead
                return f"[Privacy Protected - {title.split('-')[-1].strip() if '-' in title else 'Sensitive'}]"
        
        # Also redact if title looks like it contains credentials
        if any(char in title for char in ['@', 'password', 'pass:']):
            return "[Privacy Protected - Credentials]"
        
        # Truncate very long titles (they often contain full URLs with sensitive params)
        if len(title) > 100:
            return title[:100] + "..."
        
        return title
    
    def log_activity(self, window_info, duration):
        """Log window activity to database"""
        if not window_info:
            return
        
        category, is_productive = self.categorize_activity(window_info['app_name'], window_info['title'])
        
        # Sanitize window title for privacy
        safe_title = self.sanitize_window_title(window_info['title'])
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO window_activity 
                (window_title, app_name, app_path, duration_seconds, category, is_productive)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                safe_title,  # ✅ SANITIZED TITLE
                window_info['app_name'],
                window_info['app_path'],
                duration,
                category,
                is_productive
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️  Error logging activity: {e}")
    
    def start_tracking(self):
        """Start the tracking loop"""
        # Check if already running
        if self.is_already_running():
            print("⚠️  Tracker is already running!")
            print(f"📁 PID file exists: {self.pid_file}")
            print("💡 Use 'Stop Observation' to stop the existing tracker first")
            return
        
        # Write PID file
        self.write_pid_file()
        
        self.tracking_enabled = True
        self.last_check_time = time.time()
        
        # Log session start
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tracking_sessions (start_time, total_entries)
            VALUES (?, 0)
        """, (datetime.now(),))
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print("🟢 Tracking started! Press Ctrl+C to stop.")
        print(f"📊 Check interval: {self.config['check_interval_seconds']} seconds")
        
        try:
            while self.tracking_enabled and not self.shutdown_requested:
                current_time = time.time()
                window_info = self.get_active_window_info()
                
                if window_info:
                    # Check if window changed
                    if self.current_window != window_info['title']:
                        # Log previous window activity
                        if self.current_window:
                            duration = current_time - self.last_check_time
                            self.log_activity(window_info, duration)
                            
                            # Show sanitized title in console
                            safe_title = self.sanitize_window_title(window_info['title'])
                            print(f"⏱️  {window_info['app_name']}: {safe_title[:50]}")
                        
                        self.current_window = window_info['title']
                        self.last_check_time = current_time
                
                # Check for shutdown signal
                if self.shutdown_requested:
                    print("🛑 Shutdown requested, stopping gracefully...")
                    break
                
                time.sleep(self.config['check_interval_seconds'])
        
        except KeyboardInterrupt:
            print("\n🛑 Stopping tracker...")
            self.stop_tracking(session_id)
    
    def stop_tracking(self, session_id=None):
        """Stop tracking and save session"""
        self.tracking_enabled = False
        
        print("💾 Saving final data...")
        
        # Log final activity
        if self.current_window:
            try:
                duration = time.time() - self.last_check_time
                window_info = self.get_active_window_info()
                if window_info:
                    self.log_activity(window_info, duration)
                    print("✅ Final activity logged")
            except Exception as e:
                print(f"⚠️  Error logging final activity: {e}")
        
        # Update session end time
        if session_id:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE tracking_sessions 
                    SET end_time = ?, 
                        total_entries = (SELECT COUNT(*) FROM window_activity 
                                        WHERE timestamp >= (SELECT start_time FROM tracking_sessions WHERE id = ?))
                    WHERE id = ?
                """, (datetime.now(), session_id, session_id))
                conn.commit()
                conn.close()
                print("✅ Session data saved")
            except Exception as e:
                print(f"⚠️  Error updating session: {e}")
        
        # Remove PID file
        self.remove_pid_file()
        
        print("✅ Tracking stopped gracefully!")
    
    def is_already_running(self):
        """Check if tracker is already running with improved detection"""
        if not self.pid_file.exists():
            return False
        
        max_retries = 3
        retry_delay = 0.05
        
        for attempt in range(max_retries):
            try:
                with open(self.pid_file, 'r') as f:
                    pid_str = f.read().strip()
                    
                    if not pid_str:
                        print(f"⚠️  PID file is empty")
                        self.remove_pid_file()
                        return False
                    
                    try:
                        pid = int(pid_str)
                    except ValueError:
                        print(f"⚠️  Invalid PID in file: {pid_str}")
                        self.remove_pid_file()
                        return False
                
                # Check if process exists
                import psutil
                
                if not psutil.pid_exists(pid):
                    print(f"🧹 Removing stale PID file (process {pid} not found)")
                    self.remove_pid_file()
                    return False
                
                # Process exists, verify it's actually our tracker
                try:
                    proc = psutil.Process(pid)
                    cmdline = ' '.join(proc.cmdline())
                    
                    # Verify it's actually our tracker script
                    if 'tracker.py' in cmdline or 'tracker' in proc.name().lower():
                        print(f"⚠️  Tracker already running (PID: {pid})")
                        print(f"    Process: {proc.name()}")
                        print(f"    Command: {cmdline[:100]}...")
                        return True
                    else:
                        # PID exists but it's not our tracker
                        print(f"🧹 PID {pid} exists but is not tracker (it's {proc.name()})")
                        self.remove_pid_file()
                        return False
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    # Process exists but we can't access it or it just died
                    print(f"⚠️  Cannot verify process {pid}: {e}")
                    # Remove stale PID file to be safe
                    self.remove_pid_file()
                    return False
                
            except FileNotFoundError:
                # PID file disappeared between check and read
                return False
                
            except PermissionError:
                print(f"⚠️  Permission denied reading PID file (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    # Can't read PID file, assume stale and try to remove
                    try:
                        self.remove_pid_file()
                    except:
                        pass
                    return False
                    
            except Exception as e:
                print(f"⚠️  Error checking PID file (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    # If we can't read/parse PID file, assume it's stale
                    try:
                        self.remove_pid_file()
                    except:
                        pass
                    return False
        
        return False
    
    def write_pid_file(self):
        """Write current process ID to file with file locking to prevent race conditions"""
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                # Ensure parent directory exists
                self.pid_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Open file in write mode
                with open(self.pid_file, 'w') as f:
                    # Apply file lock based on platform
                    lock_acquired = False
                    
                    if HAS_FCNTL:
                        # Linux/Mac: Use fcntl for file locking
                        try:
                            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                            lock_acquired = True
                        except (IOError, OSError):
                            if attempt < max_retries - 1:
                                time.sleep(retry_delay * (2 ** attempt))
                                continue
                            else:
                                raise
                    
                    elif HAS_MSVCRT:
                        # Windows: Use msvcrt for file locking
                        try:
                            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                            lock_acquired = True
                        except (IOError, OSError):
                            if attempt < max_retries - 1:
                                time.sleep(retry_delay * (2 ** attempt))
                                continue
                            else:
                                raise
                    else:
                        # No locking available, proceed anyway
                        lock_acquired = True
                    
                    if lock_acquired:
                        # Write PID
                        pid = os.getpid()
                        f.write(str(pid))
                        f.flush()
                        os.fsync(f.fileno())  # Force write to disk
                        
                        print(f"📝 PID file created: {self.pid_file} (PID: {pid})")
                        return True
                
            except PermissionError:
                print(f"⚠️  Permission denied when writing PID file (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                else:
                    print(f"❌ Failed to write PID file after {max_retries} attempts")
                    return False
                    
            except Exception as e:
                print(f"⚠️  Error writing PID file (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                else:
                    print(f"❌ Failed to write PID file: {e}")
                    return False
        
        return False
    
    def remove_pid_file(self):
        """Remove PID file with retry logic"""
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                if self.pid_file.exists():
                    self.pid_file.unlink()
                    print(f"🗑️  PID file removed: {self.pid_file}")
                    return True
                else:
                    # File doesn't exist, consider it success
                    return True
                    
            except PermissionError:
                print(f"⚠️  Permission denied when removing PID file (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                else:
                    print(f"❌ Failed to remove PID file after {max_retries} attempts")
                    return False
                    
            except Exception as e:
                print(f"⚠️  Error removing PID file (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                else:
                    print(f"❌ Failed to remove PID file: {e}")
                    return False
        
        return False


def main():
    """Main entry point"""
    print("=" * 60)
    print("  PRODUCTIVITY TRACKER - Window Activity Monitor")
    print("=" * 60)
    
    tracker = WindowTracker()
    tracker.start_tracking()


if __name__ == "__main__":
    main()

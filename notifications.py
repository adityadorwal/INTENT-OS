#!/usr/bin/env python3
"""
Desktop Notification System
Cross-platform notifications for Windows, macOS, and Linux
"""

import os
import sys
import platform
from enum import Enum
from logger_config import get_logger

logger = get_logger(__name__)


class NotificationType(Enum):
    """Notification types with corresponding icons"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    COMMAND = "command"


class NotificationManager:
    """
    Cross-platform notification manager
    Automatically detects OS and uses appropriate notification method
    """
    
    def __init__(self):
        self.system = platform.system()
        self.enabled = True
        
        # Try to import platform-specific libraries
        self.notifier = None
        self._setup_notifier()
        
        logger.info(f"NotificationManager initialized for {self.system}")
    
    def _setup_notifier(self):
        """Setup platform-specific notifier"""
        try:
            if self.system == "Windows":
                self._setup_windows()
            elif self.system == "Darwin":  # macOS
                self._setup_macos()
            elif self.system == "Linux":
                self._setup_linux()
            else:
                logger.warning(f"Unsupported platform: {self.system}")
                self.enabled = False
        except Exception as e:
            logger.error(f"Failed to setup notifier: {e}")
            self.enabled = False
    
    def _setup_windows(self):
        """Setup Windows notifications"""
        try:
            # Try plyer first - more stable, no WNDPROC errors
            from plyer import notification
            self.notifier = notification
            logger.info("Plyer notification ready (Windows)")
        except ImportError:
            logger.warning("plyer not installed, trying win10toast...")
            try:
                from win10toast import ToastNotifier
                self.notifier = ToastNotifier()
                logger.info("Windows ToastNotifier ready")
            except ImportError:
                logger.error("No notification library available for Windows")
                self.enabled = False
    
    def _setup_macos(self):
        """Setup macOS notifications"""
        try:
            from pync import Notifier
            self.notifier = Notifier
            logger.info("macOS pync Notifier ready")
        except ImportError:
            logger.warning("pync not installed, trying plyer...")
            try:
                from plyer import notification
                self.notifier = notification
                logger.info("Plyer notification ready")
            except ImportError:
                logger.error("No notification library available for macOS")
                self.enabled = False
    
    def _setup_linux(self):
        """Setup Linux notifications"""
        try:
            from plyer import notification
            self.notifier = notification
            logger.info("Linux plyer notification ready")
        except ImportError:
            # Fallback to notify-send command
            if os.system("which notify-send > /dev/null 2>&1") == 0:
                self.notifier = "notify-send"
                logger.info("Using notify-send for Linux notifications")
            else:
                logger.error("No notification method available for Linux")
                self.enabled = False
    
    def show(self, title, message, notification_type=NotificationType.INFO, duration=5):
        """
        Show a desktop notification
        
        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification (INFO, SUCCESS, WARNING, ERROR, COMMAND)
            duration: Duration in seconds (default: 5)
        """
        if not self.enabled:
            logger.debug(f"Notifications disabled: {title} - {message}")
            return
        
        try:
            # Add emoji based on notification type
            emoji = self._get_emoji(notification_type)
            title_with_emoji = f"{emoji} {title}"
            
            if self.system == "Windows":
                self._show_windows(title_with_emoji, message, duration)
            elif self.system == "Darwin":
                self._show_macos(title_with_emoji, message, duration)
            elif self.system == "Linux":
                self._show_linux(title_with_emoji, message, duration)
            
            logger.debug(f"Notification shown: {title}")
            
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")
    
    def _get_emoji(self, notification_type):
        """Get emoji for notification type"""
        emoji_map = {
            NotificationType.INFO: "ℹ️",
            NotificationType.SUCCESS: "✅",
            NotificationType.WARNING: "⚠️",
            NotificationType.ERROR: "❌",
            NotificationType.COMMAND: "🎤"
        }
        return emoji_map.get(notification_type, "ℹ️")
    
    def _show_windows(self, title, message, duration):
        """Show Windows notification"""
        if hasattr(self.notifier, 'show_toast'):
            # win10toast
            self.notifier.show_toast(
                title,
                message,
                duration=duration,
                threaded=True
            )
        else:
            # plyer
            self.notifier.notify(
                title=title,
                message=message,
                timeout=duration
            )
    
    def _show_macos(self, title, message, duration):
        """Show macOS notification"""
        if hasattr(self.notifier, 'notify'):
            # pync
            self.notifier.notify(
                message,
                title=title,
                sound='default'
            )
        else:
            # plyer
            self.notifier.notify(
                title=title,
                message=message,
                timeout=duration
            )
    
    def _show_linux(self, title, message, duration):
        """Show Linux notification"""
        if self.notifier == "notify-send":
            # Use notify-send command
            os.system(f'notify-send "{title}" "{message}" -t {duration * 1000}')
        else:
            # plyer
            self.notifier.notify(
                title=title,
                message=message,
                timeout=duration
            )
    
    # Convenience methods
    
    def info(self, title, message, duration=5):
        """Show info notification"""
        self.show(title, message, NotificationType.INFO, duration)
    
    def success(self, title, message, duration=5):
        """Show success notification"""
        self.show(title, message, NotificationType.SUCCESS, duration)
    
    def warning(self, title, message, duration=5):
        """Show warning notification"""
        self.show(title, message, NotificationType.WARNING, duration)
    
    def error(self, title, message, duration=5):
        """Show error notification"""
        self.show(title, message, NotificationType.ERROR, duration)
    
    def command(self, title, message, duration=3):
        """Show command execution notification"""
        self.show(title, message, NotificationType.COMMAND, duration)
    
    def enable(self):
        """Enable notifications"""
        self.enabled = True
        logger.info("Notifications enabled")
    
    def disable(self):
        """Disable notifications"""
        self.enabled = False
        logger.info("Notifications disabled")
    
    def toggle(self):
        """Toggle notifications on/off"""
        self.enabled = not self.enabled
        status = "enabled" if self.enabled else "disabled"
        logger.info(f"Notifications {status}")
        return self.enabled


# Global notification manager instance
_notification_manager = None


def get_notification_manager():
    """Get global notification manager instance"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager


# Convenience functions for quick notifications

def notify_info(title, message, duration=5):
    """Show info notification"""
    get_notification_manager().info(title, message, duration)


def notify_success(title, message, duration=5):
    """Show success notification"""
    get_notification_manager().success(title, message, duration)


def notify_warning(title, message, duration=5):
    """Show warning notification"""
    get_notification_manager().warning(title, message, duration)


def notify_error(title, message, duration=5):
    """Show error notification"""
    get_notification_manager().error(title, message, duration)


def notify_command(title, message, duration=3):
    """Show command execution notification"""
    get_notification_manager().command(title, message, duration)


# Specific notification helpers for common scenarios

def notify_voice_command_recognized(command):
    """Notify when voice command is recognized"""
    notify_command(
        "Voice Command Recognized",
        f"Processing: {command[:50]}..."
    )


def notify_command_executed(command, success=True):
    """Notify when command is executed"""
    if success:
        notify_success(
            "Command Executed",
            f"✓ {command[:50]}..."
        )
    else:
        notify_error(
            "Command Failed",
            f"✗ {command[:50]}..."
        )


def notify_observer_status(started=True):
    """Notify Observer tracking status"""
    if started:
        notify_success(
            "Observer Tracking Started",
            "Now tracking your productivity"
        )
    else:
        notify_info(
            "Observer Tracking Stopped",
            "Tracking has been paused"
        )


def notify_whatsapp_sent(contact, success=True):
    """Notify WhatsApp message status"""
    if success:
        notify_success(
            "WhatsApp Message Sent",
            f"Message sent to {contact}"
        )
    else:
        notify_error(
            "WhatsApp Send Failed",
            f"Failed to send message to {contact}"
        )


def notify_form_filled(form_name=""):
    """Notify when form is auto-filled"""
    notify_success(
        "Form Auto-Filled",
        f"Successfully filled: {form_name or 'web form'}"
    )


def notify_file_operation(operation, filename, success=True):
    """Notify file operation status"""
    if success:
        notify_success(
            f"File {operation.title()}",
            f"✓ {filename}"
        )
    else:
        notify_error(
            f"File {operation.title()} Failed",
            f"✗ {filename}"
        )


def notify_system_command(command, success=True):
    """Notify system command execution"""
    if success:
        notify_success(
            "System Command",
            f"✓ {command}"
        )
    else:
        notify_error(
            "System Command Failed",
            f"✗ {command}"
        )


if __name__ == "__main__":
    # Test notifications
    print("Testing notifications...")
    
    nm = get_notification_manager()
    
    print("\n1. Testing INFO notification...")
    nm.info("Test Info", "This is an info notification")
    
    import time
    time.sleep(2)
    
    print("2. Testing SUCCESS notification...")
    nm.success("Test Success", "This is a success notification")
    
    time.sleep(2)
    
    print("3. Testing WARNING notification...")
    nm.warning("Test Warning", "This is a warning notification")
    
    time.sleep(2)
    
    print("4. Testing ERROR notification...")
    nm.error("Test Error", "This is an error notification")
    
    time.sleep(2)
    
    print("5. Testing COMMAND notification...")
    nm.command("Test Command", "Voice command recognized")
    
    print("\n✅ All notifications sent!")
    print("Check your system notification area to see them.")
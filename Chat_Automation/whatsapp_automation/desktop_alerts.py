"""
Desktop Alert System - Non-blocking
Shows alerts without interrupting bot
"""

import platform
import time
from datetime import datetime
import os


class DesktopAlertSystem:
    """Lightweight alert system"""
    
    def __init__(self):
        self.system = platform.system()
        self.setup_notifications()
    
    def setup_notifications(self):
        """Setup notification system"""
        try:
            from plyer import notification
            self.has_plyer = True
            self.notification = notification
        except ImportError:
            self.has_plyer = False
    
    def send_detection_alert(self, contact, message):
        """Send detection alert"""
        print("\n" + "="*60)
        print("🚨 DETECTION ALERT!")
        print("="*60)
        print(f"Contact: {contact}")
        print(f"Message: {message}")
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        print("="*60 + "\n")
        
        # Desktop notification
        if self.has_plyer:
            try:
                self.notification.notify(
                    title='🚨 BOT DETECTION!',
                    message=f'{contact}: {message[:100]}',
                    app_name='WhatsApp Bot',
                    timeout=10
                )
            except:
                pass
        
        # Sound alert
        self.play_sound()
    
    def send_summary_alert(self, contact, summary):
        """Send conversation summary"""
        print("\n" + "="*60)
        print(f"📊 CONVERSATION SUMMARY - {contact}")
        print("="*60)
        print(summary)
        print("="*60 + "\n")
        
        if self.has_plyer:
            try:
                self.notification.notify(
                    title=f'📊 Chat Summary - {contact}',
                    message='Conversation summary ready!',
                    app_name='WhatsApp Bot',
                    timeout=10
                )
            except:
                pass
    
    def play_sound(self):
        """Play alert sound"""
        try:
            if self.system == 'Windows':
                import winsound
                for _ in range(3):
                    winsound.MessageBeep(winsound.MB_ICONHAND)
                    time.sleep(0.3)
            else:
                print('\a')  # Beep
        except:
            pass
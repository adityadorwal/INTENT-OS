#!/usr/bin/env python3
"""
Voice Command System - Background Desktop App
- Small draggable microphone button for voice commands
- Left click: Toggle listening on/off
- Right click: Menu with options
- Uses Google Speech Recognition (requires internet)
- Multi-language support
"""

import sys
import os
import subprocess
import threading
import time
import urllib.request
import psutil

from PyQt5.QtWidgets import (QApplication, QWidget, QMenu, QAction, 
                              QInputDialog, QLineEdit, QMessageBox, 
                              QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QObject, QTimer
from PyQt5.QtGui import QPainter, QColor, QRadialGradient, QLinearGradient, QFont

# Import our components
from Intent_classifier import IntentClassifier, Intent
from Intent_OS import IntentOS

import speech_recognition as sr

# Import logging
from logger_config import get_main_logger, log_error

# Import notifications only (NO audio feedback)
from notifications import get_notification_manager, notify_voice_command_recognized

# Initialize logger
logger = get_main_logger()

# Initialize notification manager only
notification_manager = get_notification_manager()


class CommandConfirmationDialog(QWidget):
    """
    Beautiful floating dialog near mic button to confirm voice commands
    Modern design with glassmorphism effect
    """
    
    # Signals
    command_confirmed = pyqtSignal(str, str)  # command, mode
    command_cancelled = pyqtSignal()
    
    def __init__(self, command_text, mode, mic_button_pos, parent=None):
        super().__init__(parent)
        self.command_text = command_text
        self.mode = mode
        self.countdown = 3  # Changed from 5 to 3 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        
        self.setup_ui(mic_button_pos)
        self.timer.start(1000)  # Update every second
    
    def setup_ui(self, mic_button_pos):
        """Setup the beautiful confirmation dialog UI"""
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container frame with modern styling
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
            }
        """)
        
        # Add shadow effect
        from PyQt5.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 5)
        container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title with icon and gradient
        title_layout = QHBoxLayout()
        title_icon = QLabel("🎤")
        title_icon.setStyleSheet("font-size: 24px;")
        
        title = QLabel("Command Recognized")
        title.setStyleSheet("""
            font-size: 15px;
            font-weight: 600;
            color: #667eea;
            letter-spacing: 0.5px;
        """)
        
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Editable text field - modern design
        self.text_edit = QLineEdit()
        self.text_edit.setText(self.command_text)
        self.text_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid #e0e7ff;
                border-radius: 10px;
                font-size: 14px;
                background: white;
                color: #1e293b;
                selection-background-color: #667eea;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
                background: #f8fafc;
            }
        """)
        # Select all text on focus for easy editing
        self.text_edit.selectAll()
        self.text_edit.setFocus()
        # When user starts editing, stop the timer
        self.text_edit.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.text_edit)
        
        # Countdown label with progress indicator
        countdown_container = QHBoxLayout()
        countdown_container.setSpacing(8)
        
        self.countdown_icon = QLabel("⏱️")
        self.countdown_icon.setStyleSheet("font-size: 16px;")
        
        self.countdown_label = QLabel(f"Auto-executing in {self.countdown} seconds")
        self.countdown_label.setStyleSheet("""
            color: #64748b;
            font-size: 12px;
            font-weight: 500;
        """)
        self.countdown_label.setAlignment(Qt.AlignLeft)
        
        countdown_container.addWidget(self.countdown_icon)
        countdown_container.addWidget(self.countdown_label)
        countdown_container.addStretch()
        layout.addLayout(countdown_container)
        
        # Buttons with modern styling
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                color: #475569;
                border: 2px solid #e2e8f0;
                padding: 10px 20px;
                border-radius: 10px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #e2e8f0;
                border: 2px solid #cbd5e1;
            }
            QPushButton:pressed {
                background: #cbd5e1;
            }
        """)
        cancel_btn.clicked.connect(self.cancel_command)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        
        proceed_btn = QPushButton("✓ Proceed")
        proceed_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                padding: 10px 25px;
                border-radius: 10px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5568d3, stop:1 #6941a3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4c5cbf, stop:1 #5d3b8f);
            }
        """)
        proceed_btn.clicked.connect(self.proceed_command)
        proceed_btn.setCursor(Qt.PointingHandCursor)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(proceed_btn)
        layout.addLayout(button_layout)
        
        container.setLayout(layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        
        # Position near mic button
        self.setFixedWidth(380)
        self.adjustSize()
        
        # Position to the left of mic button with some spacing
        x = mic_button_pos.x() - self.width() - 25
        y = mic_button_pos.y() - 10
        
        # Make sure it doesn't go off-screen
        screen = QApplication.primaryScreen().geometry()
        if x < 10:
            x = mic_button_pos.x() + 90  # Show on right if left doesn't fit
        if y < 10:
            y = 10
        if y + self.height() > screen.height() - 10:
            y = screen.height() - self.height() - 10
            
        self.move(x, y)
    
    def on_text_changed(self):
        """Stop countdown when user edits text"""
        if self.timer.isActive():
            self.timer.stop()
            self.countdown_icon.setText("✏️")
            self.countdown_label.setText("Edited - click Proceed to execute")
            self.countdown_label.setStyleSheet("""
                color: #667eea;
                font-size: 12px;
                font-weight: 600;
            """)
    
    def update_countdown(self):
        """Update countdown timer with visual feedback"""
        self.countdown -= 1
        
        if self.countdown <= 0:
            # Auto-proceed
            self.timer.stop()
            self.proceed_command()
        else:
            # Update label with urgency colors
            if self.countdown <= 2:
                self.countdown_label.setStyleSheet("""
                    color: #ef4444;
                    font-size: 12px;
                    font-weight: 600;
                """)
            elif self.countdown <= 3:
                self.countdown_label.setStyleSheet("""
                    color: #f59e0b;
                    font-size: 12px;
                    font-weight: 600;
                """)
            
            self.countdown_label.setText(f"Auto-executing in {self.countdown} second{'s' if self.countdown > 1 else ''}")
    
    def proceed_command(self):
        """Proceed with command"""
        self.timer.stop()
        command = self.text_edit.text().strip()
        if command:
            self.command_confirmed.emit(command, self.mode)
        self.close()
    
    def cancel_command(self):
        """Cancel command"""
        self.timer.stop()
        self.command_cancelled.emit()
        self.close()
    
    def paintEvent(self, event):
        """Custom paint for rounded corners"""
        pass  # Styling handled by QSS


class VoiceWorker(QObject):
    """Background thread worker for voice recognition"""
    
    # Signals for communication with main thread
    error_signal = pyqtSignal(str, str)  # title, message
    transcription_signal = pyqtSignal(str, str)  # text, mode
    stopped_signal = pyqtSignal()  # auto-stop signal when auto-stopped due to silence
    
    def __init__(self, recognizer, language):
        super().__init__()
        self.recognizer = recognizer
        self.language = language
        self.is_running = False
        
    def start_recognition(self):
        """Main voice recognition loop"""
        self.is_running = True
        silence_start = None
        
        with sr.Microphone() as source:
            # Calibrate microphone for ambient noise - longer duration for better accuracy
            print("[INFO] Calibrating microphone for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
            print(f"[INFO] Auto-detected energy threshold: {self.recognizer.energy_threshold}")
            print("[INFO] Listening...")
            
            while self.is_running:
                try:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)
                    
                    # Try to recognize speech
                    try:
                        text = self.recognizer.recognize_google(audio, language=self.language)
                        self.transcription_signal.emit(text, "voice")
                        silence_start = None  # Reset silence timer on success
                        
                    except sr.UnknownValueError:
                        # Speech not understood, continue listening
                        continue
                        
                    except sr.RequestError as e:
                        # Network error occurred
                        print(f"[ERROR] Network error: {e}")
                        self.error_signal.emit(
                            "Network Error",
                            "Please check your internet connection"
                        )
                        self.is_running = False
                        break
                    
                except sr.WaitTimeoutError:
                    # Handle silence detection
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > 4:
                        # Auto-stop after 4 seconds of silence
                        self.is_running = False
                        self.stopped_signal.emit()
                        break
                
                except Exception as e:
                    # Handle other errors gracefully
                    print(f"[ERROR] Recognition error: {e}")
                    continue
    
    def stop(self):
        """Stop the recognition loop"""
        self.is_running = False


class FloatingMicButton(QWidget):
    """Small draggable microphone button"""
    
    def __init__(self):
        super().__init__()
        self.is_listening = False
        self.dragging = False
        self.offset = QPoint()
        self.observation_mode = False
        self.drag_start_pos = QPoint()
        self.mouse_press_time = 0
        
        # Speech recognition - AUTO-ADAPTIVE (works on any PC/microphone)
        self.recognizer = sr.Recognizer()
        # Removed hardcoded energy_threshold - let it auto-detect for each device
        self.recognizer.pause_threshold = 0.8
        self.recognizer.dynamic_energy_threshold = True  # Auto-adjusts to environment
        
        # Silence timeout (configurable)
        self.silence_timeout = 4.0  # seconds
        
        self.worker = None
        self.worker_thread = None
        
        # Command confirmation dialog
        self.confirmation_dialog = None
        
        # Language settings
        self.current_language = "en-US"
        self.supported_languages = {
            "English (US)": "en-US",
            "English (UK)": "en-GB",
            "Hindi": "hi-IN",
            "Spanish": "es-ES",
            "French": "fr-FR",
            "German": "de-DE",
            "Italian": "it-IT",
            "Portuguese": "pt-PT",
            "Russian": "ru-RU",
            "Chinese": "zh-CN",
            "Japanese": "ja-JP",
            "Korean": "ko-KR",
            "Arabic": "ar-SA"
        }
        
        self.setup_ui()
        self.test_microphone()
        
        # Initialize Intent Classifier and Intent_OS
        try:
            self.intent_os = IntentOS()
            self.intent_classifier = IntentClassifier()
            # Pass Intent_OS instance to classifier
            self.intent_classifier.intent_os = self.intent_os
            print("[✓] Intent Classifier and Intent_OS initialized successfully")
        except Exception as e:
            print(f"[✗] Failed to initialize components: {e}")
            self.intent_classifier = None
            self.intent_os = None
    
    def setup_ui(self):
        """Setup the floating button"""
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setFixedSize(70, 70)
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 100, 50)
        
        self.update_tooltip()
    
    def test_microphone(self):
        """Test if microphone is available"""
        try:
            mic = sr.Microphone()
            with mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.5)  # Longer calibration
            print(f"[OK] Microphone working | Language: {self.current_language}")
            print(f"[INFO] Auto-detected energy threshold: {self.recognizer.energy_threshold}")
        except Exception as e:
            print(f"[ERROR] Microphone test failed: {e}")
            QMessageBox.critical(
                self,
                "Microphone Error",
                f"Cannot access microphone:\n{str(e)}\n\nPlease check:\n"
                "- Microphone is connected\n"
                "- Permissions are granted\n"
                "- No other app is using it"
            )
    
    def check_internet(self):
        """Check if internet is available"""
        try:
            urllib.request.urlopen('https://www.google.com', timeout=2)
            return True
        except:
            return False
    
    def paintEvent(self, event):
        """Draw a beautiful modern microphone button"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Modern color scheme
        if self.is_listening:
            gradient_start = QColor(239, 68, 68)
            gradient_end = QColor(220, 38, 38)
            glow_color = QColor(239, 68, 68, 100)
        else:
            gradient_start = QColor(99, 102, 241)
            gradient_end = QColor(79, 70, 229)
            glow_color = QColor(99, 102, 241, 80)
        
        # Draw outer glow
        glow_gradient = QRadialGradient(35, 35, 40)
        glow_gradient.setColorAt(0, glow_color)
        glow_gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(glow_gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 70, 70)
        
        # Draw main button
        gradient = QLinearGradient(0, 10, 0, 60)
        gradient.setColorAt(0, gradient_start)
        gradient.setColorAt(1, gradient_end)
        
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(10, 10, 50, 50)
        
        # Draw highlight
        highlight = QRadialGradient(35, 25, 25)
        highlight.setColorAt(0, QColor(255, 255, 255, 40))
        highlight.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(highlight)
        painter.drawEllipse(10, 10, 50, 50)
        
        # Draw microphone icon
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255))
        
        if self.is_listening:
            # Active mic with sound waves
            painter.drawRoundedRect(31, 23, 8, 14, 4, 4)
            painter.drawRect(34, 37, 2, 6)
            painter.drawRoundedRect(30, 43, 10, 2, 1, 1)
            
            painter.setPen(QColor(255, 255, 255, 200))
            painter.setBrush(Qt.NoBrush)
            painter.drawArc(20, 26, 8, 8, 30 * 16, 120 * 16)
            painter.drawArc(16, 24, 12, 12, 30 * 16, 120 * 16)
            painter.drawArc(12, 22, 16, 16, 30 * 16, 120 * 16)
            painter.drawArc(42, 26, 8, 8, 30 * 16, 120 * 16)
            painter.drawArc(46, 24, 12, 12, 30 * 16, 120 * 16)
            painter.drawArc(50, 22, 16, 16, 30 * 16, 120 * 16)
        else:
            # Idle mic
            painter.drawRoundedRect(31, 23, 8, 14, 4, 4)
            painter.drawRect(34, 37, 2, 6)
            painter.drawRoundedRect(30, 43, 10, 2, 1, 1)
            
            painter.setPen(QColor(255, 255, 255, 180))
            painter.setBrush(Qt.NoBrush)
            painter.drawArc(28, 32, 14, 10, 0, -180 * 16)
        
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
            self.drag_start_pos = event.globalPos()
            self.mouse_press_time = time.time()
            self.dragging = False
    
    def contextMenuEvent(self, event):
        """Handle right click - show menu"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ccc;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #667eea;
                color: white;
            }
        """)
        
        # Settings Option
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        # Manual Command Input
        manual_cmd = QAction("📝 Manual Command Input", self)
        manual_cmd.triggered.connect(self.show_manual_input)
        menu.addAction(manual_cmd)
        
        menu.addSeparator()
        
        # ✨ Auto Form Filler
        form_filler_action = QAction("📋 Auto Form Filler", self)
        form_filler_action.triggered.connect(self.launch_form_filler)
        menu.addAction(form_filler_action)
        
        menu.addSeparator()
        
        # 🤖 WhatsApp Bot Control (NEW)
        whatsapp_bot_menu = menu.addMenu("🤖 WhatsApp Bot")
        
        # Check bot status
        try:
            from whatsapp_bot_bridge import get_whatsapp_bot
            bot = get_whatsapp_bot()
            is_bot_running = bot.is_running()
        except:
            is_bot_running = False
        
        # Start Bot
        start_bot_action = QAction("▶️ Start Bot", self)
        start_bot_action.triggered.connect(self.start_whatsapp_bot)
        start_bot_action.setEnabled(not is_bot_running)
        whatsapp_bot_menu.addAction(start_bot_action)
        
        # Stop Bot
        stop_bot_action = QAction("⏹️ Stop Bot", self)
        stop_bot_action.triggered.connect(self.stop_whatsapp_bot)
        stop_bot_action.setEnabled(is_bot_running)
        whatsapp_bot_menu.addAction(stop_bot_action)
        
        whatsapp_bot_menu.addSeparator()
        
        # Bot Status
        status_text = "🟢 Running" if is_bot_running else "🔴 Stopped"
        status_action = QAction(f"Status: {status_text}", self)
        status_action.triggered.connect(self.show_whatsapp_bot_status)
        whatsapp_bot_menu.addAction(status_action)
        
        menu.addSeparator()
        
        # 🔐 Security Menu (Phase 2 - NEW)
        security_menu = menu.addMenu("🔐 Security")
        
        # Check if security system is available
        try:
            from security_manager import get_security_manager
            security = get_security_manager()
            security_available = True
            security_enabled = security.security_enabled
            pin_set = security.is_pin_set()
        except:
            security_available = False
            security_enabled = False
            pin_set = False
        
        if security_available:
            # Setup/Change PIN
            pin_text = "🔑 Change PIN" if pin_set else "🔑 Setup PIN"
            pin_action = QAction(pin_text, self)
            pin_action.triggered.connect(self.manage_security_pin)
            security_menu.addAction(pin_action)
            
            security_menu.addSeparator()
            
            # Enable/Disable Security
            security_toggle_text = "✅ Security: ON" if security_enabled else "⚪ Security: OFF"
            security_toggle = QAction(security_toggle_text, self)
            security_toggle.triggered.connect(self.toggle_security)
            security_menu.addAction(security_toggle)
            
            security_menu.addSeparator()
            
            # Security Info
            info_action = QAction("ℹ️ Security Info", self)
            info_action.triggered.connect(self.show_security_info)
            security_menu.addAction(info_action)
        else:
            unavailable_action = QAction("⚠️ Security Unavailable", self)
            unavailable_action.setEnabled(False)
            security_menu.addAction(unavailable_action)
        
        menu.addSeparator()
        
        # Language Selection
        lang_menu = menu.addMenu("🌐 Language")
        for lang_name, lang_code in self.supported_languages.items():
            lang_action = QAction(lang_name, self)
            lang_action.setCheckable(True)
            lang_action.setChecked(lang_code == self.current_language)
            lang_action.triggered.connect(
                lambda checked, code=lang_code, name=lang_name: 
                self.change_language(code, name)
            )
            lang_menu.addAction(lang_action)
        
        menu.addSeparator()
        
        # Quit App
        quit_action = QAction("❌ Quit App", self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        menu.addSeparator()
        
        # Observation Mode
        obs_text = "🔴 Observation: ON" if self.observation_mode else "⚪ Observation: OFF"
        obs_action = QAction(obs_text, self)
        obs_action.triggered.connect(self.toggle_observation_mode)
        menu.addAction(obs_action)
        
        menu.exec_(event.globalPos())
    
    def change_language(self, lang_code, lang_name):
        """Change recognition language"""
        if self.is_listening:
            QMessageBox.warning(
                self,
                "Cannot Change Language",
                "Please stop listening before changing language."
            )
            return
        
        self.current_language = lang_code
        print(f"\n[INFO] Language changed to: {lang_name} ({lang_code})")
        self.update_tooltip()
    
    def update_tooltip(self):
        """Update tooltip"""
        self.setToolTip(f"Click: {'Stop' if self.is_listening else 'Start'} | Right: Menu | Lang: {self.current_language}")
    
    def quit_app(self):
        """Quit application with comprehensive cleanup (Phase 6)"""
        print("\n" + "="*60)
        print("   INITIATING SHUTDOWN SEQUENCE")
        print("="*60)
        
        # 1. Stop Observer tracker if it's running
        self._cleanup_observer()
        
        # 2. Stop WhatsApp bot if it's running
        self._cleanup_whatsapp_bot()
        
        # 3. Clean temporary files
        self._cleanup_temp_files()
        
        # 4. Clean Chrome profiles
        self._cleanup_chrome_profiles()
        
        # 5. Remove PID files
        self._cleanup_pid_files()
        
        # 6. Stop voice worker if running
        if self.worker:
            print("[INFO] Stopping voice recognition worker...")
            self.worker.stop()
            print("[SUCCESS] Voice worker stopped!")
        
        print("\n" + "="*60)
        print("   CLEANUP COMPLETE - GOODBYE!")
        print("="*60)
        QApplication.quit()
        sys.exit(0)
    
    def _cleanup_observer(self):
        """Stop Observer tracker process"""
        print("\n[1/5] Stopping Observer tracker...")
        try:
            from pathlib import Path
            import psutil
            
            observer_dir = Path(__file__).parent / "Observer"
            pid_file = observer_dir / "tracker.pid"
            
            if pid_file.exists():
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                try:
                    process = psutil.Process(pid)
                    process.terminate()
                    process.wait(timeout=3)
                    print("      ✅ Observer tracker stopped!")
                except psutil.NoSuchProcess:
                    print("      ℹ️  Observer already stopped")
                except psutil.TimeoutExpired:
                    process.kill()
                    print("      ✅ Observer tracker force killed!")
                
                # Remove PID file
                pid_file.unlink()
            else:
                print("      ℹ️  Observer not running")
        except Exception as e:
            print(f"      ⚠️  Could not stop Observer: {e}")
    
    def _cleanup_whatsapp_bot(self):
        """Stop WhatsApp bot process"""
        print("\n[2/5] Stopping WhatsApp bot...")
        try:
            from whatsapp_bot_bridge import get_whatsapp_bot
            bot = get_whatsapp_bot()
            
            if bot.is_running():
                bot.cleanup()
                print("      ✅ WhatsApp bot stopped!")
            else:
                print("      ℹ️  WhatsApp bot not running")
        except Exception as e:
            print(f"      ⚠️  Could not stop WhatsApp bot: {e}")
    
    def _cleanup_temp_files(self):
        """Remove temporary files and caches"""
        print("\n[3/5] Cleaning temporary files...")
        try:
            from pathlib import Path
            import shutil
            
            project_root = Path(__file__).parent
            cleaned_count = 0
            
            # Patterns to clean
            temp_patterns = [
                '*.tmp',
                '*.log.backup',
                '*.pyc'
            ]
            
            # Clean files matching patterns
            for pattern in temp_patterns:
                for file in project_root.rglob(pattern):
                    try:
                        if file.is_file():
                            file.unlink()
                            cleaned_count += 1
                    except Exception as e:
                        pass  # Skip files we can't delete
            
            # Clean __pycache__ directories (but not the main ones we need)
            for pycache in project_root.rglob('__pycache__'):
                # Skip if in main project directories we want to keep
                if pycache.parent.name in ['final working project', 'Observer', 'Chat_Automation']:
                    continue
                try:
                    shutil.rmtree(pycache)
                    cleaned_count += 1
                except:
                    pass
            
            if cleaned_count > 0:
                print(f"      ✅ Cleaned {cleaned_count} temporary files")
            else:
                print("      ℹ️  No temporary files to clean")
        except Exception as e:
            print(f"      ⚠️  Temp file cleanup error: {e}")
    
    def _cleanup_chrome_profiles(self):
        """Clean orphaned Chrome profile lock files"""
        print("\n[4/5] Cleaning Chrome profiles...")
        try:
            from pathlib import Path
            
            cleaned = 0
            
            # WhatsApp profile
            wa_profile = Path(__file__).parent / "Chat_Automation" / "whatsapp_profile"
            if wa_profile.exists():
                lock_files = list(wa_profile.rglob("*Lock*"))
                lock_files.extend(list(wa_profile.rglob("*.lock")))
                
                for lock in lock_files:
                    try:
                        lock.unlink()
                        cleaned += 1
                    except:
                        pass
            
            # ChatGPT profile
            gpt_profile = Path(__file__).parent / "Chat_Automation" / "chatgpt_profile"
            if gpt_profile.exists():
                lock_files = list(gpt_profile.rglob("*Lock*"))
                lock_files.extend(list(gpt_profile.rglob("*.lock")))
                
                for lock in lock_files:
                    try:
                        lock.unlink()
                        cleaned += 1
                    except:
                        pass
            
            if cleaned > 0:
                print(f"      ✅ Cleaned {cleaned} Chrome lock files")
            else:
                print("      ℹ️  No Chrome locks to clean")
        except Exception as e:
            print(f"      ⚠️  Chrome cleanup error: {e}")
    
    def _cleanup_pid_files(self):
        """Remove all PID files"""
        print("\n[5/5] Removing PID files...")
        try:
            from pathlib import Path
            
            project_root = Path(__file__).parent
            pid_files = list(project_root.rglob("*.pid"))
            
            removed = 0
            for pid_file in pid_files:
                try:
                    pid_file.unlink()
                    removed += 1
                except:
                    pass
            
            if removed > 0:
                print(f"      ✅ Removed {removed} PID files")
            else:
                print("      ℹ️  No PID files to remove")
        except Exception as e:
            print(f"      ⚠️  PID cleanup error: {e}")
    
    def launch_form_filler(self):
        """Launch Auto Form Filler"""
        try:
            print("\n[INFO] Launching Auto Form Filler...")
            
            # Get the directory where main.py is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Path to form filler launcher - CORRECT PATH IN AUTO_FORM_FILLER SUBDIRECTORY
            launcher_script = os.path.join(script_dir, "Auto_Form_Filler", "form_filler_launcher.py")
            
            # Check if launcher exists
            if not os.path.exists(launcher_script):
                print(f"[ERROR] Form filler launcher not found: {launcher_script}")
                
                # Try alternate location (for backwards compatibility)
                alt_launcher = os.path.join(script_dir, "form_filler_launcher.py")
                if os.path.exists(alt_launcher):
                    launcher_script = alt_launcher
                    print(f"[INFO] Using alternate launcher: {launcher_script}")
                else:
                    QMessageBox.critical(
                        self,
                        "Form Filler Not Found",
                        f"Auto Form Filler is not installed.\n\n"
                        f"Expected location:\n{launcher_script}\n\n"
                    f"Please make sure form_filler_launcher.py is in the same folder as main.py"
                )
                return
            
            # Launch the form filler launcher
            subprocess.Popen(
                [sys.executable, launcher_script],
                cwd=script_dir
            )
            
            print("[SUCCESS] ✅ Auto Form Filler launched!")
            print("[INFO] A window should open where you can paste the form URL")
            
        except Exception as e:
            print(f"[ERROR] Failed to launch form filler: {e}")
            QMessageBox.critical(
                self,
                "Launch Error",
                f"Failed to launch Auto Form Filler:\n{str(e)}"
            )
    
    def start_whatsapp_bot(self):
        """Start WhatsApp automated chatbot"""
        try:
            print("\n[INFO] Starting WhatsApp bot...")
            
            from whatsapp_bot_bridge import get_whatsapp_bot
            bot = get_whatsapp_bot()
            
            if bot.is_running():
                QMessageBox.information(
                    self,
                    "Bot Already Running",
                    "WhatsApp bot is already running!"
                )
                return
            
            success = bot.start_bot()
            
            if success:
                QMessageBox.information(
                    self,
                    "Bot Started",
                    "WhatsApp bot started successfully!\n\n"
                    "The bot window should open shortly."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Start Failed",
                    "Failed to start WhatsApp bot.\n\n"
                    "Check console for details."
                )
        
        except Exception as e:
            print(f"[ERROR] Failed to start WhatsApp bot: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to start WhatsApp bot:\n{str(e)}"
            )
    
    def stop_whatsapp_bot(self):
        """Stop WhatsApp automated chatbot"""
        try:
            print("\n[INFO] Stopping WhatsApp bot...")
            
            from whatsapp_bot_bridge import get_whatsapp_bot
            bot = get_whatsapp_bot()
            
            if not bot.is_running():
                QMessageBox.information(
                    self,
                    "Bot Not Running",
                    "WhatsApp bot is not currently running."
                )
                return
            
            success = bot.stop_bot()
            
            if success:
                QMessageBox.information(
                    self,
                    "Bot Stopped",
                    "WhatsApp bot stopped successfully!"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Stop Failed",
                    "Failed to stop WhatsApp bot.\n\n"
                    "Check console for details."
                )
        
        except Exception as e:
            print(f"[ERROR] Failed to stop WhatsApp bot: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to stop WhatsApp bot:\n{str(e)}"
            )
    
    def show_whatsapp_bot_status(self):
        """Show WhatsApp bot status"""
        try:
            from whatsapp_bot_bridge import get_whatsapp_bot
            bot = get_whatsapp_bot()
            
            status = bot.get_status()
            
            status_msg = f"Status: {status['status_text']}\n\n"
            
            if status['running'] and 'pid' in status:
                status_msg += f"Process ID: {status['pid']}\n"
            
            if status['running']:
                status_msg += "\nThe bot is actively monitoring WhatsApp messages."
            else:
                status_msg += "\nUse 'Start Bot' to begin automated responses."
            
            QMessageBox.information(
                self,
                "WhatsApp Bot Status",
                status_msg
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Status Error",
                f"Failed to get bot status:\n{str(e)}"
            )
    
    def manage_security_pin(self):
        """Setup or change security PIN"""
        try:
            from security_manager import get_security_manager
            security = get_security_manager()
            
            if security.is_pin_set():
                # Change existing PIN
                success = security.change_pin(parent=self)
                if success:
                    logger.info("Security PIN changed successfully")
            else:
                # Setup new PIN
                success = security.setup_pin(parent=self)
                if success:
                    logger.info("Security PIN setup successfully")
        
        except Exception as e:
            logger.error(f"PIN management error: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to manage PIN:\n{str(e)}"
            )
    
    def toggle_security(self):
        """Enable or disable security system"""
        try:
            from security_manager import get_security_manager
            security = get_security_manager()
            
            current_state = security.security_enabled
            new_state = not current_state
            
            if new_state:
                # Enabling security
                if not security.is_pin_set():
                    response = QMessageBox.question(
                        self,
                        "Setup PIN Required",
                        "Security requires a PIN to be set.\n\n"
                        "Would you like to set one now?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if response == QMessageBox.Yes:
                        if security.setup_pin(parent=self):
                            security.enable_security(True)
                            QMessageBox.information(
                                self,
                                "Security Enabled",
                                "Security system is now active!\n\n"
                                "You'll be asked for PIN for:\n"
                                "• Deleting files\n"
                                "• Closing applications\n"
                                "• System operations"
                            )
                            logger.info("Security enabled")
                    else:
                        return
                else:
                    security.enable_security(True)
                    QMessageBox.information(
                        self,
                        "Security Enabled",
                        "Security system is now active!"
                    )
                    logger.info("Security enabled")
            else:
                # Disabling security - require PIN
                if security.is_pin_set():
                    if not security.verify_pin(parent=self, action_description="disabling security"):
                        return
                
                security.enable_security(False)
                QMessageBox.information(
                    self,
                    "Security Disabled",
                    "Security system is now disabled.\n\n"
                    "All operations will proceed without PIN verification."
                )
                logger.info("Security disabled")
        
        except Exception as e:
            logger.error(f"Security toggle error: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to toggle security:\n{str(e)}"
            )
    
    def show_security_info(self):
        """Show security system information"""
        try:
            from security_manager import get_security_manager
            security = get_security_manager()
            
            enabled = "✅ Enabled" if security.security_enabled else "❌ Disabled"
            pin_status = "✅ Configured" if security.is_pin_set() else "❌ Not Set"
            
            info_text = f"""
🔐 SECURITY SYSTEM STATUS

Status: {enabled}
PIN: {pin_status}

SECURITY TIERS:

📗 Tier 1 (Low Risk): No confirmation needed
• Reading information, searching files
• Asking questions, checking status

📘 Tier 2 (Medium Risk): Simple confirmation
• Sending messages, opening apps
• Web browsing, organizing files
• Taking screenshots

📙 Tier 3 (High Risk): PIN required
• Deleting files
• Closing applications
• Downloading files

📕 Tier 4 (Critical): PIN + Warning
• Shutdown/Restart
• System sleep
• Quitting application

PROTECTION:
Security protects you from accidentally executing
dangerous voice commands, especially:
• File deletion
• System operations
• Application termination

SETUP:
1. Setup PIN: Creates 4-digit PIN
2. Enable Security: Activates protection
3. Voice commands will request PIN when needed

Keep your PIN secure!
"""
            
            QMessageBox.information(
                self,
                "🔐 Security System",
                info_text
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to get security info:\n{str(e)}"
            )
    
    def show_settings(self):
        """Show settings dialog"""
        try:
            from settings_dialog import SettingsDialog
            
            dialog = SettingsDialog(self)
            dialog.settings_changed.connect(self.on_settings_changed)
            
            if dialog.exec_() == dialog.Accepted:
                print("[INFO] Settings saved successfully")
                notification_manager.success(
                    "Settings Updated",
                    "Your settings have been saved"
                )
            
        except Exception as e:
            logger.error(f"Failed to show settings: {e}")
            QMessageBox.critical(
                self,
                "Settings Error",
                f"Failed to open settings:\n{str(e)}"
            )
    
    def on_settings_changed(self):
        """Handle settings changes"""
        logger.info("Settings changed - reloading configuration")
        
        # Reload config
        try:
            import json
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            # Update feature states
            features = config.get('features', {})
            
            # Update notification state
            if 'notifications' in features:
                if features['notifications']:
                    notification_manager.enable()
                else:
                    notification_manager.disable()
            
            # NO audio feedback - removed
            
            logger.info("Configuration reloaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
    
    def show_manual_input(self):
        """Show manual input dialog"""
        text, ok = QInputDialog.getText(
            self,
            'Manual Command Input',
            'Enter your command:',
            QLineEdit.Normal,
            ''
        )
        
        if ok and text.strip():
            print("\n" + "="*60)
            print("[MANUAL COMMAND INPUT]")
            print("-"*60)
            print(text.strip())
            print("="*60 + "\n")
            self.handle_transcription(text.strip(), "manual")
    
    def toggle_observation_mode(self):
        """Toggle observation mode - ACTUALLY CONTROL TRACKER.PY"""
        from pathlib import Path
        import psutil  # ADD THIS - needed for process management
        
        self.observation_mode = not self.observation_mode
        status = "ON" if self.observation_mode else "OFF"
        print(f"\n[OBSERVATION MODE] {status}")
        
        # Path to tracker.py and PID file
        observer_dir = os.path.join(os.path.dirname(__file__), "Observer")
        tracker_path = os.path.join(observer_dir, "tracker.py")
        pid_file = os.path.join(observer_dir, "tracker.pid")
        
        if self.observation_mode:
            # START TRACKING
            print("[INFO] Starting Observer tracker...")
            
            # Check if already running
            if os.path.exists(pid_file):
                try:
                    with open(pid_file, 'r') as f:
                        old_pid = int(f.read().strip())
                    print(f"[INFO] Found existing PID file (PID: {old_pid})")
                    print("[INFO] Stopping old tracker first...")
                    
                    # Try to kill old process
                    try:
                        import psutil
                        if psutil.pid_exists(old_pid):
                            proc = psutil.Process(old_pid)
                            proc.terminate()
                            proc.wait(timeout=5)
                            print("[SUCCESS] Old tracker stopped")
                    except:
                        pass
                    
                    # Remove stale PID file
                    if os.path.exists(pid_file):
                        os.remove(pid_file)
                        time.sleep(0.5)
                        
                except Exception as e:
                    print(f"[WARNING] Error cleaning up old tracker: {e}")
            
            try:
                # Start tracker.py as independent background process
                if os.name == 'nt':  # Windows
                    pythonw_path = sys.executable.replace('python.exe', 'pythonw.exe')
                    if not os.path.exists(pythonw_path):
                        pythonw_path = sys.executable
                    
                    # Use CREATE_NEW_PROCESS_GROUP to allow clean termination
                    import subprocess
                    DETACHED_PROCESS = 0x00000008
                    CREATE_NEW_PROCESS_GROUP = 0x00000200
                    
                    subprocess.Popen(
                        [pythonw_path, tracker_path],
                        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                        cwd=observer_dir
                    )
                else:  # Linux/Mac
                    subprocess.Popen(
                        [sys.executable, tracker_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        preexec_fn=os.setsid,
                        cwd=observer_dir
                    )
                
                # Wait a moment for process to start
                time.sleep(1)
                
                # Verify it started
                if os.path.exists(pid_file):
                    print("[SUCCESS] ✅ Observer tracking started!")
                    print("[INFO] 📊 Productivity monitoring is now active")
                    print("[INFO] 🔒 Window titles are sanitized for privacy")
                    
                    # Show notification
                    from notifications import notify_observer_status
                    notify_observer_status(started=True)
                else:
                    print("[WARNING] Tracker may not have started properly")
                    print("[INFO] Check Observer folder for errors")
                    
            except Exception as e:
                print(f"[ERROR] Failed to start tracker: {e}")
                self.observation_mode = False
                
        else:
            # STOP TRACKING
            print("[INFO] Stopping Observer tracker...")
            
            try:
                if os.path.exists(pid_file):
                    # Read PID
                    with open(pid_file, 'r') as f:
                        pid = int(f.read().strip())
                    
                    print(f"[INFO] Found tracker process (PID: {pid})")
                    
                    # Send graceful termination signal
                    try:
                        # psutil is already imported at top, don't re-import
                        if psutil.pid_exists(pid):
                            proc = psutil.Process(pid)
                            
                            print("[INFO] Sending shutdown signal...")
                            proc.terminate()  # Sends SIGTERM (graceful)
                            
                            # Wait for graceful shutdown
                            try:
                                proc.wait(timeout=5)
                                print("[SUCCESS] ✅ Tracker stopped gracefully")
                            except psutil.TimeoutExpired:
                                print("[WARNING] Tracker didn't stop gracefully, forcing...")
                                proc.kill()  # Force kill if needed
                                print("[SUCCESS] Tracker force stopped")
                        else:
                            print("[INFO] Process not found (already stopped)")
                            
                    except Exception as e:
                        print(f"[ERROR] Error stopping process: {e}")
                    
                    # Clean up PID file
                    if os.path.exists(pid_file):
                        os.remove(pid_file)
                        print("[INFO] PID file cleaned up")
                        
                else:
                    print("[INFO] No PID file found (tracker not running)")
                    print("[INFO] Attempting cleanup anyway...")
                    
                    # Fallback: try to find and kill tracker processes
                    if os.name == 'nt':  # Windows
                        subprocess.run(
                            ['taskkill', '/F', '/IM', 'pythonw.exe', '/FI', 'WINDOWTITLE eq tracker.py*'],
                            capture_output=True, text=True
                        )
                    else:  # Linux/Mac
                        subprocess.run(['pkill', '-f', 'tracker.py'], capture_output=True, text=True)
                
                print("[SUCCESS] ✅ Observer tracking stopped!")
                
                # Show notification
                from notifications import notify_observer_status
                notify_observer_status(started=False)
                
            except Exception as e:
                print(f"[ERROR] Failed to stop tracker: {e}")
                print("[INFO] You may need to manually kill the process")
        
        print("[INFO] Observation mode toggle complete\n")
            
    def mouseMoveEvent(self, event):
        """Handle dragging"""
        if event.buttons() == Qt.LeftButton:
            distance = (event.globalPos() - self.drag_start_pos).manhattanLength()
            if distance > 10:
                self.dragging = True
                self.move(self.mapToGlobal(event.pos() - self.offset))
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            press_duration = time.time() - self.mouse_press_time
            distance = (event.globalPos() - self.drag_start_pos).manhattanLength()
            
            if distance < 10 and press_duration < 0.5:
                self.toggle_listening()
            
            self.dragging = False
    
    def toggle_listening(self):
        """Toggle voice recognition"""
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()
    
    def start_listening(self):
        """Start voice recognition"""
        if not self.check_internet():
            QMessageBox.warning(
                self,
                "No Internet Connection",
                "Please connect to the internet to use voice recognition."
            )
            print("\n[ERROR] No internet connection!\n")
            return
        
        if self.worker_thread and self.worker_thread.is_alive():
            return
            
        self.is_listening = True
        self.update()
        self.update_tooltip()
        
        # NO notification for listening start (user requested removal)
        # notification_manager.info("Voice Recognition", "Listening...")
        
        print("\n" + "="*60)
        print("[STARTED] Voice recognition active")
        print(f"[INFO] Language: {self.current_language}")
        print("="*60)
        
        # Create worker and thread
        self.worker = VoiceWorker(self.recognizer, self.current_language)
        self.worker.transcription_signal.connect(self.handle_transcription)
        self.worker.error_signal.connect(self.show_error)
        self.worker.stopped_signal.connect(self.handle_auto_stop)
        
        self.worker_thread = threading.Thread(
            target=self.worker.start_recognition,
            daemon=True
        )
        self.worker_thread.start()
    
    def stop_listening(self):
        """Stop voice recognition"""
        if self.worker:
            self.worker.stop()
        self.is_listening = False
        self.update()
        self.update_tooltip()
        
        # NO audio feedback - silent operation
        
        print("\n[STOPPED] Voice recognition stopped\n")
    
    def handle_auto_stop(self):
        """Handle automatic stop due to silence"""
        self.is_listening = False
        self.update()
        self.update_tooltip()
        print("\n[AUTO-STOPPED] Microphone off (4s silence)\n")
    
    def handle_transcription(self, text, mode):
        """Process recognized speech - NOW SHOWS CONFIRMATION DIALOG"""
        if mode == "voice":
            # Stop listening after receiving command
            self.stop_listening()
            
            # Show notification (NO audio)
            notify_voice_command_recognized(text)
            
            # Show confirmation dialog near mic button
            self.show_confirmation_dialog(text, mode)
        else:
            # Manual commands - direct execution
            self.process_confirmed_command(text, mode)
    
    def show_confirmation_dialog(self, command_text, mode):
        """Show command confirmation dialog near mic button"""
        # Close existing dialog if any
        if self.confirmation_dialog:
            self.confirmation_dialog.close()
        
        # Create new confirmation dialog
        mic_pos = self.pos()
        self.confirmation_dialog = CommandConfirmationDialog(
            command_text, 
            mode, 
            mic_pos, 
            self
        )
        
        # Connect signals
        self.confirmation_dialog.command_confirmed.connect(self.process_confirmed_command)
        self.confirmation_dialog.command_cancelled.connect(self.handle_cancelled_command)
        
        # Show dialog
        self.confirmation_dialog.show()

    
    def process_confirmed_command(self, command, mode):
        """Process a confirmed command through intent classifier"""
        print("\n" + "="*60)
        print(f"[PROCESSING COMMAND - {mode.upper()}]")
        print("-"*60)
        print(f"Command: {command}")
        print("="*60 + "\n")
        
        # Pass to Intent Classifier if available
        if self.intent_classifier:
            try:
                # Just classify and let intent classifier handle printing
                intent = self.intent_classifier.classify(command)
                
                # Handle quit commands directly
                if "quit" in command.lower() or "exit" in command.lower():
                    print("[RESPONSE] Goodbye!")
                    self.quit_app()
                    
            except Exception as e:
                print(f"[❌] Intent classification failed: {e}")
        else:
            print("[❌] Intent Classifier not available")
        
        print("="*60 + "\n")
    
    def handle_cancelled_command(self):
        """Handle cancelled command"""
        print("[CANCELLED] Command was cancelled by user")
    
    def show_error(self, title, message):
        """Show error dialog (called from worker thread)"""
        self.stop_listening()
        QMessageBox.critical(self, title, message)


def main():
    logger.info("="*60)
    logger.info("Voice Command System - Starting Application")
    logger.info("="*60)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    print("="*60)
    print("     VOICE COMMAND SYSTEM - Background App")
    print("="*60)
    print("\n[INFO] Starting...")
    print("[INFO] Google Speech Recognition (internet required)")
    print("[INFO] Multi-language support available")
    print("[INFO] Left click: Toggle | Right click: Menu")
    print("[INFO] Commands processed immediately")
    print("\nPress Ctrl+C to quit\n")
    
    logger.info("Initializing floating microphone button")
    button = FloatingMicButton()
    button.show()
    
    logger.info("Application ready - entering event loop")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Settings Dialog - Configuration UI
Allows users to modify:
- API Keys
- Language preferences
- Feature toggles
- Form filler data
- Notification preferences
"""

import os
import json
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox,
    QGroupBox, QFormLayout, QMessageBox, QScrollArea,
    QTextEdit, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from logger_config import get_logger

logger = get_logger(__name__)


class SettingsDialog(QDialog):
    """
    Comprehensive settings dialog for the Voice Command System
    """
    
    # Signal emitted when settings are saved
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings - Voice Command System")
        self.setMinimumSize(700, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Paths to config files
        self.config_path = "config.json"
        self.form_data_path = "Auto_Form_Filler/user_data.json"
        self.env_path = ".env"
        
        # Load current settings
        self.config_data = self.load_config()
        self.form_data = self.load_form_data()
        self.env_data = self.load_env_file()
        
        self.setup_ui()
        self.load_current_values()
        
    def setup_ui(self):
        """Setup the dialog UI with tabs"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
            }
            QTabBar::tab {
                background: #f0f0f0;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: white;
                border: 1px solid #ddd;
                border-bottom: none;
            }
        """)
        
        # Add tabs
        self.tabs.addTab(self.create_api_tab(), "🔑 API Keys")
        self.tabs.addTab(self.create_language_tab(), "🌐 Language")
        self.tabs.addTab(self.create_features_tab(), "⚙️ Features")
        self.tabs.addTab(self.create_form_data_tab(), "📝 Form Data")
        self.tabs.addTab(self.create_advanced_tab(), "🔧 Advanced")
        self.tabs.addTab(self.create_observer_tab(), "🗄️ Observer")
        
        layout.addWidget(self.tabs)
        
        # Add buttons at bottom
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save Settings")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #dc2626;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_api_tab(self):
        """Create API Keys configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Scroll area for API keys
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        
        # API Keys Group
        api_group = QGroupBox("API Keys Configuration")
        api_layout = QFormLayout()
        
        self.api_inputs = {}
        api_providers = [
            ("gemini", "Google Gemini"),
            ("groq", "Groq"),
            ("deepseek", "DeepSeek"),
            ("huggingface", "Hugging Face"),
            ("cohere", "Cohere"),
            ("mistral", "Mistral AI")
        ]
        
        for key, label in api_providers:
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"Enter your {label} API key...")
            input_field.setEchoMode(QLineEdit.Password)
            
            # Add toggle to show/hide
            show_btn = QPushButton("👁️")
            show_btn.setFixedWidth(40)
            show_btn.setCheckable(True)
            show_btn.toggled.connect(
                lambda checked, field=input_field: 
                field.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
            )
            
            container = QHBoxLayout()
            container.addWidget(input_field)
            container.addWidget(show_btn)
            
            api_layout.addRow(f"{label}:", container)
            self.api_inputs[key] = input_field
        
        api_group.setLayout(api_layout)
        scroll_layout.addWidget(api_group)
        
        # API Priority Group
        priority_group = QGroupBox("API Priority Order")
        priority_layout = QVBoxLayout()
        
        priority_info = QLabel("Drag to reorder (first = highest priority):")
        priority_info.setStyleSheet("color: #666; font-style: italic;")
        priority_layout.addWidget(priority_info)
        
        self.priority_list = QComboBox()
        self.priority_list.setEditable(False)
        priority_layout.addWidget(self.priority_list)
        
        priority_group.setLayout(priority_layout)
        scroll_layout.addWidget(priority_group)
        
        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        
        layout.addWidget(scroll)
        widget.setLayout(layout)
        return widget
    
    def create_language_tab(self):
        """Create Language settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Language Selection Group
        lang_group = QGroupBox("Voice Recognition Language")
        lang_layout = QFormLayout()
        
        self.language_combo = QComboBox()
        languages = [
            ("English (US)", "en-US"),
            ("English (UK)", "en-GB"),
            ("Hindi", "hi-IN"),
            ("Spanish", "es-ES"),
            ("French", "fr-FR"),
            ("German", "de-DE"),
            ("Italian", "it-IT"),
            ("Portuguese", "pt-PT"),
            ("Russian", "ru-RU"),
            ("Chinese", "zh-CN"),
            ("Japanese", "ja-JP"),
            ("Korean", "ko-KR"),
            ("Arabic", "ar-SA")
        ]
        
        for name, code in languages:
            self.language_combo.addItem(name, code)
        
        lang_layout.addRow("Language:", self.language_combo)
        
        # Add info label
        info = QLabel("⚠️ Changes will apply to next voice recognition session")
        info.setStyleSheet("color: #f59e0b; font-style: italic;")
        lang_layout.addRow("", info)
        
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_features_tab(self):
        """Create Features toggle tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Features Group
        features_group = QGroupBox("Feature Toggles")
        features_layout = QVBoxLayout()
        
        self.feature_checkboxes = {}
        features = [
            ("voice_recognition", "🎤 Voice Recognition", "Enable/disable voice command system"),
            ("observer_tracking", "👁️ Observer Tracking", "Track productivity and app usage"),
            ("whatsapp_automation", "💬 WhatsApp Automation", "Automated WhatsApp messaging"),
            ("form_filling", "📝 Auto Form Filling", "Automatically fill web forms"),
            ("notifications", "🔔 Desktop Notifications", "Show notifications for actions"),
            ("audio_feedback", "🔊 Audio Feedback", "Play sounds for voice commands")
        ]
        
        for key, label, description in features:
            checkbox = QCheckBox(label)
            checkbox.setStyleSheet("font-weight: bold;")
            
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #666; margin-left: 25px; font-size: 11px;")
            
            features_layout.addWidget(checkbox)
            features_layout.addWidget(desc_label)
            features_layout.addSpacing(10)
            
            self.feature_checkboxes[key] = checkbox
        
        features_group.setLayout(features_layout)
        layout.addWidget(features_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_form_data_tab(self):
        """Create Form Filler Data tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Personal Info
        personal_group = QGroupBox("Personal Information")
        personal_layout = QFormLayout()
        
        self.form_inputs = {}
        
        personal_fields = [
            ("full_name", "Full Name"),
            ("first_name", "First Name"),
            ("last_name", "Last Name"),
            ("email", "Email"),
            ("phone", "Phone"),
            ("date_of_birth", "Date of Birth"),
            ("gender", "Gender"),
            ("address", "Address"),
            ("city", "City"),
            ("state", "State"),
            ("country", "Country"),
            ("zip_code", "ZIP Code"),
            ("nationality", "Nationality")
        ]
        
        for key, label in personal_fields:
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"Enter your {label.lower()}...")
            personal_layout.addRow(f"{label}:", input_field)
            self.form_inputs[f"personal_info.{key}"] = input_field
        
        personal_group.setLayout(personal_layout)
        scroll_layout.addWidget(personal_group)
        
        # Education Info
        education_group = QGroupBox("Education")
        education_layout = QFormLayout()
        
        education_fields = [
            ("highest_degree", "Highest Degree"),
            ("institution", "Institution"),
            ("major", "Major/Field"),
            ("graduation_year", "Graduation Year"),
            ("gpa", "GPA/Percentage")
        ]
        
        for key, label in education_fields:
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"Enter your {label.lower()}...")
            education_layout.addRow(f"{label}:", input_field)
            self.form_inputs[f"education.{key}"] = input_field
        
        education_group.setLayout(education_layout)
        scroll_layout.addWidget(education_group)
        
        # Professional Info
        professional_group = QGroupBox("Professional")
        professional_layout = QFormLayout()
        
        professional_fields = [
            ("occupation", "Occupation"),
            ("company", "Company"),
            ("job_title", "Job Title"),
            ("years_of_experience", "Years of Experience"),
            ("industry", "Industry")
        ]
        
        for key, label in professional_fields:
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"Enter your {label.lower()}...")
            professional_layout.addRow(f"{label}:", input_field)
            self.form_inputs[f"professional.{key}"] = input_field
        
        professional_group.setLayout(professional_layout)
        scroll_layout.addWidget(professional_group)
        
        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        
        layout.addWidget(scroll)
        widget.setLayout(layout)
        return widget
    
    def create_advanced_tab(self):
        """Create Advanced settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # API Settings
        api_settings_group = QGroupBox("API Settings")
        api_settings_layout = QFormLayout()
        
        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(1, 10)
        self.retry_spin.setValue(3)
        api_settings_layout.addRow("Retry Attempts:", self.retry_spin)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 120)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" seconds")
        api_settings_layout.addRow("Timeout:", self.timeout_spin)
        
        api_settings_group.setLayout(api_settings_layout)
        layout.addWidget(api_settings_group)
        
        # Voice Settings
        voice_group = QGroupBox("Voice Recognition Settings")
        voice_layout = QFormLayout()
        
        self.silence_timeout_spin = QDoubleSpinBox()
        self.silence_timeout_spin.setRange(1.0, 30.0)
        self.silence_timeout_spin.setValue(4.0)
        self.silence_timeout_spin.setSingleStep(0.5)
        self.silence_timeout_spin.setSuffix(" seconds")
        voice_layout.addRow("Silence Timeout:", self.silence_timeout_spin)
        
        self.energy_threshold_spin = QSpinBox()
        self.energy_threshold_spin.setRange(100, 5000)
        self.energy_threshold_spin.setValue(1200)
        self.energy_threshold_spin.setSingleStep(100)
        voice_layout.addRow("Energy Threshold:", self.energy_threshold_spin)
        
        voice_group.setLayout(voice_layout)
        layout.addWidget(voice_group)
        
        # Paths
        paths_group = QGroupBox("File Paths")
        paths_layout = QFormLayout()
        
        self.log_path_input = QLineEdit("logs")
        paths_layout.addRow("Log Directory:", self.log_path_input)
        
        self.observer_db_input = QLineEdit("Observer/productivity_data.db")
        paths_layout.addRow("Observer Database:", self.observer_db_input)
        
        paths_group.setLayout(paths_layout)
        layout.addWidget(paths_group)
        
        # Reset to Default button
        reset_btn = QPushButton("🔄 Reset All to Default Values")
        reset_btn.setStyleSheet("""
            QPushButton {
                background: #f59e0b;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: #d97706;
            }
        """)
        reset_btn.clicked.connect(self.reset_advanced_to_default)
        layout.addWidget(reset_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def reset_advanced_to_default(self):
        """Reset advanced settings to default values"""
        reply = QMessageBox.question(
            self,
            "Reset to Default",
            "Are you sure you want to reset all advanced settings to their default values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Default values
            self.retry_spin.setValue(3)
            self.timeout_spin.setValue(30)
            self.silence_timeout_spin.setValue(4.0)
            self.energy_threshold_spin.setValue(1200)
            self.log_path_input.setText("logs")
            self.observer_db_input.setText("Observer/productivity_data.db")
            
            QMessageBox.information(
                self,
                "Reset Complete",
                "✅ All advanced settings have been reset to default values."
            )
    
    def load_config(self):
        """Load config.json"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
        return {}
    
    def load_form_data(self):
        """Load form filler data"""
        try:
            if os.path.exists(self.form_data_path):
                with open(self.form_data_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load form data: {e}")
        return {}
    
    def load_env_file(self):
        """Load .env file"""
        env_data = {}
        try:
            if os.path.exists(self.env_path):
                with open(self.env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_data[key.strip()] = value.strip()
        except Exception as e:
            logger.error(f"Failed to load .env: {e}")
        return env_data
    
    def load_current_values(self):
        """Load current values into UI"""
        # Load API keys from .env
        for key, input_field in self.api_inputs.items():
            env_key = f"{key.upper()}_API_KEY"
            if env_key in self.env_data:
                input_field.setText(self.env_data[env_key])
        
        # Load features
        features = self.config_data.get('features', {})
        for key, checkbox in self.feature_checkboxes.items():
            checkbox.setChecked(features.get(key, True))
        
        # Load form data
        for key, input_field in self.form_inputs.items():
            parts = key.split('.')
            value = self.form_data
            for part in parts:
                value = value.get(part, {})
                if isinstance(value, str):
                    break
            if isinstance(value, str):
                input_field.setText(value)
        
        # Load advanced settings
        self.retry_spin.setValue(self.config_data.get('retry_attempts', 3))
        self.timeout_spin.setValue(self.config_data.get('timeout_seconds', 30))
    
    def save_settings(self):
        """Save all settings"""
        try:
            # Save API keys to .env
            env_lines = []
            for key, input_field in self.api_inputs.items():
                value = input_field.text().strip()
                if value:
                    env_key = f"{key.upper()}_API_KEY"
                    env_lines.append(f"{env_key}={value}\n")
            
            with open(self.env_path, 'w') as f:
                f.writelines(env_lines)
            
            # Save config.json
            self.config_data['features'] = {
                key: checkbox.isChecked()
                for key, checkbox in self.feature_checkboxes.items()
            }
            self.config_data['retry_attempts'] = self.retry_spin.value()
            self.config_data['timeout_seconds'] = self.timeout_spin.value()
            
            with open(self.config_path, 'w') as f:
                json.dump(self.config_data, f, indent=4)
            
            # Save form data
            for key, input_field in self.form_inputs.items():
                parts = key.split('.')
                current = self.form_data
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = input_field.text().strip()
            
            with open(self.form_data_path, 'w') as f:
                json.dump(self.form_data, f, indent=2)
            
            # Show success message
            QMessageBox.information(
                self,
                "Settings Saved",
                "✅ All settings have been saved successfully!\n\n"
                "Some changes may require restarting the application."
            )
            
            logger.info("Settings saved successfully")
            self.settings_changed.emit()
            self.accept()
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(
                self,
                "Save Failed",
                f"❌ Failed to save settings:\n{str(e)}"
            )
    
    def create_observer_tab(self):
        """Create Observer Database Cleanup tab"""
        widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Header
        header = QLabel("🗄️ Observer Database Management")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #1f2937; margin-bottom: 10px;")
        main_layout.addWidget(header)
        
        # Info label
        info_label = QLabel(
            "Clean up old Observer tracking data to free up disk space.\n"
            "This will permanently delete detailed activity records older than the selected period."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #6b7280; margin-bottom: 15px;")
        main_layout.addWidget(info_label)
        
        # Database stats group
        stats_group = QGroupBox("📊 Database Statistics")
        stats_layout = QVBoxLayout()
        
        self.db_stats_label = QLabel("Click 'Refresh Stats' to see current database information")
        self.db_stats_label.setWordWrap(True)
        self.db_stats_label.setStyleSheet("""
            QLabel {
                background: #f3f4f6;
                padding: 15px;
                border-radius: 5px;
                font-family: 'Consolas', monospace;
            }
        """)
        stats_layout.addWidget(self.db_stats_label)
        
        refresh_stats_btn = QPushButton("🔄 Refresh Stats")
        refresh_stats_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        refresh_stats_btn.clicked.connect(self.refresh_database_stats)
        stats_layout.addWidget(refresh_stats_btn)
        
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)
        
        # Cleanup options group
        cleanup_group = QGroupBox("🗑️ Cleanup Options")
        cleanup_layout = QVBoxLayout()
        
        # Cleanup period selector
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Delete data older than:"))
        
        self.cleanup_period_combo = QComboBox()
        self.cleanup_period_combo.addItems([
            "7 days (Keep 1 week)",
            "30 days (Keep 1 month)",
            "60 days (Keep 2 months)",
            "90 days (Keep 3 months)",
            "180 days (Keep 6 months)",
            "365 days (Keep 1 year)"
        ])
        self.cleanup_period_combo.setCurrentIndex(1)  # Default: 30 days
        period_layout.addWidget(self.cleanup_period_combo)
        period_layout.addStretch()
        
        cleanup_layout.addLayout(period_layout)
        
        # Preview button
        preview_btn = QPushButton("👁️ Preview Cleanup")
        preview_btn.setStyleSheet("""
            QPushButton {
                background: #8b5cf6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background: #7c3aed;
            }
        """)
        preview_btn.clicked.connect(self.preview_cleanup)
        cleanup_layout.addWidget(preview_btn)
        
        # Cleanup button
        cleanup_btn = QPushButton("🗑️ Delete Old Data")
        cleanup_btn.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 5px;
                font-weight: bold;
                margin: 5px 0;
            }
            QPushButton:hover {
                background: #dc2626;
            }
        """)
        cleanup_btn.clicked.connect(self.perform_cleanup)
        cleanup_layout.addWidget(cleanup_btn)
        
        cleanup_group.setLayout(cleanup_layout)
        main_layout.addWidget(cleanup_group)
        
        # Warning label
        warning_label = QLabel(
            "⚠️ Warning: Deleted data cannot be recovered!\n"
            "Make sure to preview cleanup before proceeding."
        )
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("""
            QLabel {
                background: #fef3c7;
                color: #92400e;
                padding: 10px;
                border-left: 4px solid #f59e0b;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(warning_label)
        
        # Spacer
        main_layout.addStretch()
        
        widget.setLayout(main_layout)
        return widget
    
    def refresh_database_stats(self):
        """Refresh and display database statistics"""
        import sqlite3
        from pathlib import Path
        from datetime import datetime, timedelta
        
        try:
            # Get database path
            observer_dir = Path("Observer")
            db_path = observer_dir / "productivity_data.db"
            
            if not db_path.exists():
                self.db_stats_label.setText("❌ Database not found!\n\nObserver database doesn't exist yet.\nTurn on Observer mode to create it.")
                return
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Total records
            cursor.execute("SELECT COUNT(*) FROM window_activity")
            total_records = cursor.fetchone()[0]
            
            # Database size
            db_size_mb = db_path.stat().st_size / (1024 * 1024)
            
            # Records by age
            periods = [
                ("Last 7 days", 7),
                ("Last 30 days", 30),
                ("Last 90 days", 90)
            ]
            
            stats_text = f"📊 DATABASE STATISTICS\n\n"
            stats_text += f"Total Records: {total_records:,}\n"
            stats_text += f"Database Size: {db_size_mb:.2f} MB\n\n"
            stats_text += "Records by Age:\n"
            
            for label, days in periods:
                cursor.execute(f"""
                    SELECT COUNT(*) FROM window_activity 
                    WHERE timestamp >= date('now', '-{days} days')
                """)
                count = cursor.fetchone()[0]
                percentage = (count / total_records * 100) if total_records > 0 else 0
                stats_text += f"  • {label:15s}: {count:6,} ({percentage:5.1f}%)\n"
            
            # Oldest record
            cursor.execute("SELECT MIN(timestamp) FROM window_activity")
            oldest = cursor.fetchone()[0]
            if oldest:
                stats_text += f"\nOldest Record: {oldest[:10]}"
            
            conn.close()
            
            self.db_stats_label.setText(stats_text)
            
        except Exception as e:
            self.db_stats_label.setText(f"❌ Error loading stats:\n{str(e)}")
    
    def preview_cleanup(self):
        """Preview what will be deleted"""
        import sqlite3
        from pathlib import Path
        from datetime import datetime, timedelta
        
        try:
            # Get selected period
            period_text = self.cleanup_period_combo.currentText()
            days = int(period_text.split()[0])
            
            # Get database path
            observer_dir = Path("Observer")
            db_path = observer_dir / "productivity_data.db"
            
            if not db_path.exists():
                QMessageBox.warning(
                    self,
                    "Database Not Found",
                    "Observer database doesn't exist yet.\nTurn on Observer mode to create it."
                )
                return
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Count records to delete
            cutoff_date = datetime.now() - timedelta(days=days)
            cursor.execute("""
                SELECT COUNT(*) FROM window_activity 
                WHERE timestamp < ?
            """, (cutoff_date,))
            
            count_to_delete = cursor.fetchone()[0]
            
            # Total records
            cursor.execute("SELECT COUNT(*) FROM window_activity")
            total_count = cursor.fetchone()[0]
            
            # Estimate space savings
            db_size_mb = db_path.stat().st_size / (1024 * 1024)
            estimated_savings = (count_to_delete / total_count) * db_size_mb if total_count > 0 else 0
            
            conn.close()
            
            if count_to_delete == 0:
                QMessageBox.information(
                    self,
                    "No Data to Delete",
                    f"No records older than {days} days found.\n\nNothing will be deleted."
                )
                return
            
            # Show preview
            preview_msg = (
                f"🗑️ CLEANUP PREVIEW\n\n"
                f"Records to delete: {count_to_delete:,} / {total_count:,}\n"
                f"Cutoff date: {cutoff_date.date()}\n"
                f"Estimated space savings: {estimated_savings:.2f} MB\n\n"
                f"Click 'Delete Old Data' to proceed."
            )
            
            QMessageBox.information(
                self,
                "Cleanup Preview",
                preview_msg
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Preview Error",
                f"Error previewing cleanup:\n{str(e)}"
            )
    
    def perform_cleanup(self):
        """Perform the actual cleanup"""
        import sqlite3
        from pathlib import Path
        from datetime import datetime, timedelta
        
        try:
            # Get selected period
            period_text = self.cleanup_period_combo.currentText()
            days = int(period_text.split()[0])
            
            # Get database path
            observer_dir = Path("Observer")
            db_path = observer_dir / "productivity_data.db"
            
            if not db_path.exists():
                QMessageBox.warning(
                    self,
                    "Database Not Found",
                    "Observer database doesn't exist yet."
                )
                return
            
            # Confirm deletion
            confirm = QMessageBox.question(
                self,
                "⚠️ Confirm Deletion",
                f"Are you sure you want to delete all data older than {days} days?\n\n"
                f"⚠️ This action cannot be undone!\n\n"
                f"Click 'Yes' to proceed with deletion.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm != QMessageBox.Yes:
                return
            
            # Perform deletion
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get size before
            size_before = db_path.stat().st_size / (1024 * 1024)
            
            # Delete
            cursor.execute("""
                DELETE FROM window_activity 
                WHERE timestamp < ?
            """, (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            # Optimize database
            cursor.execute("VACUUM")
            conn.close()
            
            # Get size after
            size_after = db_path.stat().st_size / (1024 * 1024)
            savings = size_before - size_after
            
            # Show success message
            QMessageBox.information(
                self,
                "✅ Cleanup Complete",
                f"Successfully deleted {deleted_count:,} records!\n\n"
                f"Database size before: {size_before:.2f} MB\n"
                f"Database size after: {size_after:.2f} MB\n"
                f"Space saved: {savings:.2f} MB"
            )
            
            # Refresh stats
            self.refresh_database_stats()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Cleanup Error",
                f"Error during cleanup:\n{str(e)}"
            )


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.show()
    sys.exit(app.exec_())
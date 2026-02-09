"""
Security Manager - 4-Tier Security System
Protects sensitive operations with PIN and confirmation dialogs

Tier 1 (Low Risk): No confirmation needed
Tier 2 (Medium Risk): Simple confirmation dialog
Tier 3 (High Risk): PIN verification required
Tier 4 (Critical): PIN + additional warning dialog
"""

import os
import json
import hashlib
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from PyQt5.QtWidgets import (QInputDialog, QMessageBox, QDialog, QVBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QHBoxLayout, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from logger_config import get_logger

logger = get_logger(__name__)


class SecurityManager:
    """
    4-Tier Security System for Voice Commands
    
    Tier 1: No confirmation (safe operations)
    Tier 2: Simple confirmation (medium risk)
    Tier 3: PIN required (high risk)
    Tier 4: PIN + critical warning (system operations)
    """
    
    # Security tier definitions
    SECURITY_TIERS = {
        'tier1': {
            'name': 'Low Risk',
            'description': 'Safe operations that need no confirmation',
            'actions': [
                # Conversation & Information
                'general_question', 'help', 'greeting', 'what_time',
                # Read-only operations
                'list_files', 'search_files', 'show_form_data',
                'bot_status', 'show_status', 'show_productivity',
                # Observer (read-only)
                'open_dashboard', 'generate_report',
            ],
            'requires_pin': False,
            'requires_confirmation': False,
            'critical': False
        },
        'tier2': {
            'name': 'Medium Risk',
            'description': 'Common operations that need simple confirmation',
            'actions': [
                # Messaging
                'send_message', 'open_chat',
                # Web browsing
                'search', 'play_youtube', 'open_website', 'play_spotify',
                # Apps
                'open_app',
                # File operations (non-destructive)
                'organize_files', 'move_files', 'copy_files', 
                'compress', 'extract', 'create_folder',
                # Screenshots
                'screenshot', 'take_screenshot',
                # Form filler (non-destructive)
                'start_form_filler', 'update_form_data',
                # WhatsApp bot
                'start_bot', 'restart_bot',
            ],
            'requires_pin': False,
            'requires_confirmation': True,
            'critical': False
        },
        'tier3': {
            'name': 'High Risk',
            'description': 'Potentially destructive operations requiring PIN',
            'actions': [
                # Destructive file operations
                'delete_files', 'remove_files',
                # App control
                'close_app', 'kill_app',
                # Downloads
                'download_file',
                # System cleaning
                'clean_temp',
                # Bot control
                'stop_bot',
                # Form filler
                'stop_form_filler',
            ],
            'requires_pin': True,
            'requires_confirmation': True,
            'critical': False
        },
        'tier4': {
            'name': 'Critical',
            'description': 'System-level operations requiring PIN + warning',
            'actions': [
                # System operations
                'shutdown', 'restart', 'sleep', 'hibernate', 'lock',
                # Application control
                'quit_app', 'exit',
                # Dangerous operations (if implemented)
                'format_drive', 'factory_reset', 'delete_all',
                'uninstall_app', 'modify_registry',
            ],
            'requires_pin': True,
            'requires_confirmation': True,
            'critical': True
        }
    }
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize Security Manager
        
        Args:
            config_dir: Directory for security config (default: project root)
        """
        if config_dir is None:
            config_dir = Path(__file__).parent
        
        self.config_path = config_dir / "security_config.json"
        self.config = self._load_config()
        self.pin_hash = self.config.get('pin_hash')
        self.security_enabled = self.config.get('enabled', True)
        self.failed_attempts = 0
        self.max_attempts = 3
        
        logger.info("Security Manager initialized")
        logger.info(f"Security enabled: {self.security_enabled}")
        logger.info(f"PIN configured: {bool(self.pin_hash)}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load security configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                logger.info("Security config loaded")
                return config
            except Exception as e:
                logger.error(f"Failed to load security config: {e}")
                return self._default_config()
        else:
            logger.info("No security config found, using defaults")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Get default security configuration"""
        return {
            'enabled': True,
            'pin_hash': None,
            'custom_tiers': {},  # User can reassign actions to different tiers
            'pin_timeout': 300,  # PIN valid for 5 minutes
            'last_pin_time': 0
        }
    
    def _save_config(self):
        """Save security configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info("Security config saved")
        except Exception as e:
            logger.error(f"Failed to save security config: {e}")
    
    def _hash_pin(self, pin: str) -> str:
        """
        Hash PIN for secure storage
        
        Args:
            pin: Plain text PIN
            
        Returns:
            SHA-256 hash of PIN
        """
        return hashlib.sha256(pin.encode()).hexdigest()
    
    def is_pin_set(self) -> bool:
        """Check if PIN has been configured"""
        return self.pin_hash is not None
    
    def setup_pin(self, parent: Optional[QWidget] = None) -> bool:
        """
        Initial PIN setup with confirmation
        
        Args:
            parent: Parent widget for dialogs
            
        Returns:
            True if PIN was set successfully
        """
        logger.info("Starting PIN setup")
        
        # First PIN entry
        pin, ok = QInputDialog.getText(
            parent,
            "🔐 Security Setup",
            "Create a 4-digit PIN for secure operations:\n\n"
            "This PIN will be required for:\n"
            "• Deleting files\n"
            "• Closing applications\n"
            "• System operations (shutdown, restart)\n",
            QLineEdit.Password
        )
        
        if not ok or not pin:
            logger.info("PIN setup cancelled by user")
            return False
        
        # Validate PIN format
        if not pin.isdigit() or len(pin) != 4:
            QMessageBox.warning(
                parent,
                "Invalid PIN",
                "PIN must be exactly 4 digits (0-9 only).\n\n"
                "Example: 1234"
            )
            logger.warning("PIN setup failed: invalid format")
            return False
        
        # Confirm PIN
        confirm, ok = QInputDialog.getText(
            parent,
            "Confirm PIN",
            "Re-enter your PIN to confirm:",
            QLineEdit.Password
        )
        
        if not ok or pin != confirm:
            QMessageBox.warning(
                parent,
                "PIN Mismatch",
                "The PINs you entered don't match.\n\n"
                "Please try again."
            )
            logger.warning("PIN setup failed: mismatch")
            return False
        
        # Save hashed PIN
        self.pin_hash = self._hash_pin(pin)
        self.config['pin_hash'] = self.pin_hash
        self._save_config()
        
        QMessageBox.information(
            parent,
            "✅ PIN Set Successfully",
            "Your security PIN has been set!\n\n"
            "You'll be asked for this PIN when:\n"
            "• Deleting files\n"
            "• Closing applications\n"
            "• Performing system operations\n\n"
            "Keep your PIN secure!"
        )
        
        logger.info("PIN setup completed successfully")
        return True
    
    def verify_pin(self, parent: Optional[QWidget] = None, action_description: str = "this operation") -> bool:
        """
        Verify PIN for secure operations
        
        Args:
            parent: Parent widget for dialogs
            action_description: Description of what action requires PIN
            
        Returns:
            True if PIN is correct
        """
        # If no PIN is set, prompt to set one
        if not self.pin_hash:
            response = QMessageBox.question(
                parent,
                "No PIN Set",
                f"A security PIN is required for {action_description}.\n\n"
                "Would you like to set one now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if response == QMessageBox.Yes:
                return self.setup_pin(parent)
            else:
                logger.info("PIN verification cancelled: no PIN set")
                return False
        
        # Check failed attempts
        if self.failed_attempts >= self.max_attempts:
            QMessageBox.critical(
                parent,
                "Too Many Failed Attempts",
                f"You've entered an incorrect PIN {self.max_attempts} times.\n\n"
                "For security, this operation is blocked.\n"
                "Please restart the application to try again."
            )
            logger.warning(f"PIN verification blocked: {self.failed_attempts} failed attempts")
            return False
        
        # Prompt for PIN
        remaining_attempts = self.max_attempts - self.failed_attempts
        
        pin, ok = QInputDialog.getText(
            parent,
            "🔐 Security Verification",
            f"Enter your 4-digit PIN for {action_description}:\n\n"
            f"Attempts remaining: {remaining_attempts}",
            QLineEdit.Password
        )
        
        if not ok:
            logger.info("PIN verification cancelled by user")
            return False
        
        # Verify PIN
        if self._hash_pin(pin) == self.pin_hash:
            self.failed_attempts = 0
            logger.info(f"PIN verified successfully for: {action_description}")
            return True
        else:
            self.failed_attempts += 1
            remaining = self.max_attempts - self.failed_attempts
            
            if remaining > 0:
                QMessageBox.warning(
                    parent,
                    "Incorrect PIN",
                    f"The PIN you entered is incorrect.\n\n"
                    f"Attempts remaining: {remaining}"
                )
            
            logger.warning(f"PIN verification failed. Attempts: {self.failed_attempts}/{self.max_attempts}")
            return False
    
    def change_pin(self, parent: Optional[QWidget] = None) -> bool:
        """
        Change existing PIN
        
        Args:
            parent: Parent widget for dialogs
            
        Returns:
            True if PIN was changed successfully
        """
        if not self.pin_hash:
            # No PIN set, just set new one
            return self.setup_pin(parent)
        
        # Verify old PIN first
        if not self.verify_pin(parent, "changing your PIN"):
            return False
        
        # Now set new PIN
        logger.info("Old PIN verified, setting new PIN")
        
        # Clear old hash temporarily
        old_hash = self.pin_hash
        self.pin_hash = None
        
        # Try to set new PIN
        if self.setup_pin(parent):
            logger.info("PIN changed successfully")
            return True
        else:
            # Restore old PIN if setup failed
            self.pin_hash = old_hash
            logger.info("PIN change cancelled, old PIN restored")
            return False
    
    def get_action_tier(self, action: str) -> str:
        """
        Determine security tier for an action
        
        Args:
            action: Action name (e.g., 'delete_files', 'send_message')
            
        Returns:
            Tier name ('tier1', 'tier2', 'tier3', or 'tier4')
        """
        # Check custom tier assignments first
        custom_tiers = self.config.get('custom_tiers', {})
        if action in custom_tiers:
            tier = custom_tiers[action]
            logger.debug(f"Action '{action}' assigned to custom {tier}")
            return tier
        
        # Check default tier assignments
        for tier, config in self.SECURITY_TIERS.items():
            if action in config['actions']:
                logger.debug(f"Action '{action}' assigned to default {tier}")
                return tier
        
        # Default to tier 2 (medium risk) for unknown actions
        logger.warning(f"Unknown action '{action}', defaulting to tier2")
        return 'tier2'
    
    def authorize_action(
        self, 
        action: str, 
        action_description: Optional[str] = None,
        parent: Optional[QWidget] = None
    ) -> bool:
        """
        Check if action is authorized based on security tier
        
        Args:
            action: Action name
            action_description: Human-readable description
            parent: Parent widget for dialogs
            
        Returns:
            True if action is authorized
        """
        # If security is disabled, allow everything
        if not self.security_enabled:
            logger.info(f"Security disabled, authorizing '{action}'")
            return True
        
        # Get tier and configuration
        tier = self.get_action_tier(action)
        tier_config = self.SECURITY_TIERS[tier]
        
        # Format action description
        if action_description is None:
            action_description = action.replace('_', ' ').title()
        
        logger.info(f"Authorizing '{action}' (Tier: {tier})")
        
        # Tier 1: No authorization needed
        if tier == 'tier1':
            logger.info(f"Tier 1 action '{action}' - auto-authorized")
            return True
        
        # Tier 2: Simple confirmation
        if tier == 'tier2':
            if tier_config['requires_confirmation']:
                return self._simple_confirmation(action_description, parent)
            return True
        
        # Tier 3: PIN required
        if tier == 'tier3':
            if not self.verify_pin(parent, action_description):
                logger.warning(f"PIN verification failed for '{action}'")
                return False
            
            if tier_config['requires_confirmation']:
                return self._simple_confirmation(action_description, parent)
            return True
        
        # Tier 4: PIN + critical confirmation
        if tier == 'tier4':
            if not self.verify_pin(parent, action_description):
                logger.warning(f"PIN verification failed for critical action '{action}'")
                return False
            
            return self._critical_confirmation(action_description, parent)
        
        # Should never reach here
        logger.error(f"Unknown tier '{tier}' for action '{action}'")
        return False
    
    def _simple_confirmation(self, action_description: str, parent: Optional[QWidget] = None) -> bool:
        """
        Simple confirmation dialog for medium-risk operations
        
        Args:
            action_description: Description of the action
            parent: Parent widget
            
        Returns:
            True if confirmed
        """
        reply = QMessageBox.question(
            parent,
            "Confirm Action",
            f"Execute: {action_description}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        confirmed = reply == QMessageBox.Yes
        logger.info(f"Simple confirmation for '{action_description}': {'Approved' if confirmed else 'Denied'}")
        return confirmed
    
    def _critical_confirmation(self, action_description: str, parent: Optional[QWidget] = None) -> bool:
        """
        Critical confirmation dialog with warning for high-risk operations
        
        Args:
            action_description: Description of the action
            parent: Parent widget
            
        Returns:
            True if confirmed
        """
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("⚠️ CRITICAL ACTION")
        msg.setText(f"WARNING: About to {action_description}")
        msg.setInformativeText(
            "This is a critical system operation!\n\n"
            "This action may:\n"
            "• Close all running applications\n"
            "• Affect system state\n"
            "• Require system restart\n\n"
            "Are you absolutely sure you want to proceed?"
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        
        # Make text bigger and red for emphasis
        font = QFont()
        font.setPointSize(10)
        msg.setFont(font)
        
        result = msg.exec_()
        confirmed = result == QMessageBox.Yes
        
        logger.warning(f"Critical confirmation for '{action_description}': {'APPROVED' if confirmed else 'DENIED'}")
        return confirmed
    
    def enable_security(self, enabled: bool = True):
        """
        Enable or disable security system
        
        Args:
            enabled: True to enable, False to disable
        """
        self.security_enabled = enabled
        self.config['enabled'] = enabled
        self._save_config()
        
        status = "enabled" if enabled else "disabled"
        logger.info(f"Security system {status}")
    
    def get_tier_info(self, tier: str) -> Dict[str, Any]:
        """
        Get information about a security tier
        
        Args:
            tier: Tier name ('tier1', 'tier2', etc.)
            
        Returns:
            Tier configuration dictionary
        """
        return self.SECURITY_TIERS.get(tier, {})
    
    def get_all_tiers(self) -> Dict[str, Dict[str, Any]]:
        """Get all security tier definitions"""
        return self.SECURITY_TIERS
    
    def reset_failed_attempts(self):
        """Reset failed PIN attempt counter"""
        self.failed_attempts = 0
        logger.info("Failed PIN attempts reset")


# Singleton instance
_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    """Get singleton instance of SecurityManager"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager


# Convenience functions
def authorize_action(action: str, description: Optional[str] = None, parent: Optional[QWidget] = None) -> bool:
    """Convenience function to authorize an action"""
    return get_security_manager().authorize_action(action, description, parent)


def is_security_enabled() -> bool:
    """Check if security is enabled"""
    return get_security_manager().security_enabled

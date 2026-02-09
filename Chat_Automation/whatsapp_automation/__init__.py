"""
WhatsApp Automation Package

A modular system for WhatsApp automation with two modes:
1. Automated Chatbot - Full AI-powered conversation automation
2. Manual Sender - Quick message sending

Usage:
    # Automated mode
    python automated_chatbot.py
    
    # Manual mode
    python send_message.py
    
    # Or import
    from send_message import send_whatsapp_message
"""

__version__ = "2.0.0"
__author__ = "WhatsApp Automation Team"

# Make key functions available at package level
from .send_message import send_whatsapp_message
from .chrome_manager import ChromeManager
from .whatsapp_helper import WhatsAppHelper
from .chatgpt_helper import ChatGPTHelper

__all__ = [
    'send_whatsapp_message',
    'ChromeManager',
    'WhatsAppHelper',
    'ChatGPTHelper'
]

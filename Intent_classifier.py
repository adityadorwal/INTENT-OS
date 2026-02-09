#!/usr/bin/env python3
"""
INTENT CLASSIFIER - Clean & Smart Version
Simple AI-powered intent classification for Intent_OS

This classifier takes any command and uses AI to understand:
- What the user wants to do (intent)
- What parameters they provided (entities)
- Which feature to call (action path)
"""

import sys
import os
import json
import re
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Import logging
from logger_config import get_classifier_logger, log_error

# Initialize logger
logger = get_classifier_logger()

# Import your AI handler
sys.path.insert(0, os.path.dirname(__file__))
from api_handler import APIHandler


@dataclass
class Intent:
    """Simple structure to hold classification results"""
    category: str           # Main category (e.g., "messaging", "file_ops", "web")
    action: str            # Specific action (e.g., "send_message", "open_app")
    parameters: Dict[str, Any]  # Extracted parameters
    confidence: float      # How confident we are (0.0 to 1.0)
    raw_command: str       # Original command
    
    def __str__(self):
        return f"Intent(category='{self.category}', action='{self.action}', confidence={self.confidence:.2f})"


class IntentClassifier:
    """
    Smart intent classifier using AI
    
    How it works:
    1. Takes user command
    2. Uses AI to understand what they want
    3. Extracts intent + parameters
    4. Returns clean Intent object you can use
    """
    
    def __init__(self, intent_os_instance=None):
        """Initialize the classifier with AI and optional Intent_OS instance"""
        try:
            self.ai = APIHandler()
            print("[✓] Intent Classifier initialized with AI")
        except Exception as e:
            print(f"[✗] Failed to initialize AI: {e}")
            raise
        
        # Store Intent_OS instance if provided (to avoid circular imports)
        self.intent_os = intent_os_instance
        if self.intent_os:
            print("[✓] Intent_OS instance connected")
    
    def classify(self, command: str) -> Intent:
        """
        Main method - classify any command
        
        Args:
            command: User's natural language command
            
        Returns:
            Intent object with category, action, and parameters
        """
        command = command.strip().lower()
        
        if not command:
            return Intent(
                category="unknown",
                action="none",
                parameters={},
                confidence=0.0,
                raw_command=command
            )
        
        print("[🧠] Analyzing intent...")
        
        # Use AI to understand the intent
        ai_result = self._ask_ai(command)
        
        # Create and return Intent object
        intent = Intent(
            category=ai_result.get("category", "unknown"),
            action=ai_result.get("action", "none"),
            parameters=ai_result.get("parameters", {}),
            confidence=ai_result.get("confidence", 0.5),
            raw_command=command
        )
        
        # Log the intent classification
        logger.info(f"Command classified: '{command}'")
        logger.info(f"Category: {intent.category}, Action: {intent.action}, Confidence: {intent.confidence:.2%}")
        logger.debug(f"Parameters extracted: {intent.parameters}")
        
        # Print the intent analysis results
        print(f"\n[✅] INTENT IDENTIFIED:")
        print(f"   Category:    {intent.category}")
        print(f"   Action:      {intent.action}")
        print(f"   Parameters:  {intent.parameters}")
        print(f"   Confidence:  {intent.confidence:.2%}")
        print(f"   Action Path: {self.get_action_path(intent)}")
        print(f"   Raw Command: {intent.raw_command}")
        print()
        
        # Pass intent to Intent_OS for execution
        if self.intent_os:
            try:
                logger.info("Executing intent via Intent_OS")
                print(f"[🚀] Executing intent via Intent_OS...")
                self.intent_os._route_to_handler(intent)
            except Exception as e:
                logger.error(f"Intent_OS execution failed: {e}", exc_info=True)
                log_error(f"Intent execution error: {e}")
                print(f"[❌] Intent_OS execution failed: {e}")
        else:
            logger.warning("Intent_OS not available for execution")
            print("[❌] Intent_OS not available for execution")
        
        return intent
    
    def _ask_ai(self, command: str) -> Dict[str, Any]:
        """
        Ask AI to classify command - IMPROVED PROMPT
        """
        prompt = f"""Analyze and classify this command:
"{command}"

Categories & Actions:
• messaging: send_message, open_chat
• web: search, play_youtube, open_website, play_spotify
• file_ops: organize_files, delete_files, move_files, copy_files, compress, extract
• app_control: open_app, close_app
• system: clean_temp, screenshot, shutdown, restart, lock, sleep, volume_control, quit_app
• download: download_file
• observer: show_status, show_productivity, start_tracking, stop_tracking, generate_report
• form_filler: start_form_filler, stop_form_filler, update_form_data, show_form_data
• whatsapp_bot: start_bot, stop_bot, restart_bot, bot_status
• conversation: general_question, help, greeting
• general: unknown

CRITICAL CLASSIFICATION RULES (MUST FOLLOW):
1. MESSAGING COMMANDS - ANY command with "send" + contact name + "as" + message → messaging.send_message:
   "send mummy as hello" → messaging.send_message, recipient="mummy", message="hello"
   "send message to john as hi" → messaging.send_message, recipient="john", message="hi"
   "whatsapp diksha as how are you" → messaging.send_message, recipient="diksha", message="how are you"
   "message sarah as are you free" → messaging.send_message, recipient="sarah", message="are you free"
   
2. Form filling variations → form_filler.start_form_filler:
   "start form filling", "start form filler", "fill form", "auto fill", "fill this form"
   
3. WhatsApp bot control → whatsapp_bot:
   "start whatsapp bot", "stop chatbot", "whatsapp bot status", "restart wa bot"
   
4. Quit/exit variations → system.quit_app:
   "quit", "exit", "close app", "goodbye", "bye"
   
5. General questions (ONLY use when NOT a command) → conversation.general_question:
   "what can you do", "help", "are you listening", "hello", "hi"
   
6. NEVER classify "send/message/whatsapp X as Y" as conversation - ALWAYS messaging!
7. NEVER classify form operations as app_control
8. NEVER classify quit/exit as general

Enhanced Pattern Examples:
"send diksha as hello" → {{"category":"messaging","action":"send_message","parameters":{{"recipient":"diksha","message":"hello"}},"confidence":0.95}}
"send a message to mummy as hello how are you" → {{"category":"messaging","action":"send_message","parameters":{{"recipient":"mummy","message":"hello how are you"}},"confidence":0.95}}
"message john as what's up" → {{"category":"messaging","action":"send_message","parameters":{{"recipient":"john","message":"what's up"}},"confidence":0.95}}
"whatsapp sarah as hi there" → {{"category":"messaging","action":"send_message","parameters":{{"recipient":"sarah","message":"hi there"}},"confidence":0.95}}
"start form filling" → {{"category":"form_filler","action":"start_form_filler","parameters":{{}},"confidence":0.9}}
"play despacito" → {{"category":"web","action":"play_youtube","parameters":{{"query":"despacito"}},"confidence":0.9}}
"open chrome" → {{"category":"app_control","action":"open_app","parameters":{{"app_name":"chrome"}},"confidence":0.9}}
"what can you do" → {{"category":"conversation","action":"general_question","parameters":{{"question":"what can you do"}},"confidence":0.85}}

Return ONLY JSON (no explanation):
{{"category":"...","action":"...","parameters":{{}},"confidence":0.9}}"""

        try:
            # Get AI response
            response = self.ai.send_request(prompt)
            
            # Handle different response formats
            if isinstance(response, dict):
                result = response
            elif isinstance(response, str):
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)
                else:
                    return self._fallback_classification(command)
            else:
                return self._fallback_classification(command)
            
            # Validate result
            if isinstance(result, dict) and 'category' in result:
                return result
            else:
                return self._fallback_classification(command)
                
        except Exception as e:
            print(f"[WARN] AI failed, using fallback: {e}")
            return self._fallback_classification(command)
    
    def _fallback_classification(self, command: str) -> Dict[str, Any]:
        """
        Pattern matching fallback - IMPROVED PATTERNS
        """
        cmd = command.lower().strip()
        
        # === FORM FILLER - COMPREHENSIVE PATTERNS (CHECK FIRST!) ===
        if any(phrase in cmd for phrase in [
            'form fill', 'fill form', 'auto fill', 
            'form filler', 'form filling', 'fill this form',
            'auto fill form', 'start filling'
        ]):
            if any(word in cmd for word in ['start', 'open', 'launch', 'begin']) or \
               cmd.startswith(('fill', 'auto')):
                return {
                    "category": "form_filler",
                    "action": "start_form_filler",
                    "parameters": {},
                    "confidence": 0.9
                }
            elif any(word in cmd for word in ['stop', 'close', 'end']):
                return {
                    "category": "form_filler",
                    "action": "stop_form_filler",
                    "parameters": {},
                    "confidence": 0.9
                }
        
        # === WHATSAPP BOT CONTROL PATTERNS ===
        if any(phrase in cmd for phrase in [
            'whatsapp bot', 'bot whatsapp', 'chat bot', 'chatbot', 
            'auto reply', 'automated chat', 'wa bot'
        ]):
            # Start bot
            if any(word in cmd for word in ['start', 'launch', 'open', 'begin', 'enable', 'turn on', 'activate']):
                return {
                    "category": "whatsapp_bot",
                    "action": "start_bot",
                    "parameters": {},
                    "confidence": 0.9
                }
            # Stop bot
            elif any(word in cmd for word in ['stop', 'close', 'end', 'disable', 'turn off', 'deactivate']):
                return {
                    "category": "whatsapp_bot",
                    "action": "stop_bot",
                    "parameters": {},
                    "confidence": 0.9
                }
            # Restart bot
            elif 'restart' in cmd or 'reload' in cmd:
                return {
                    "category": "whatsapp_bot",
                    "action": "restart_bot",
                    "parameters": {},
                    "confidence": 0.9
                }
            # Check status
            elif any(word in cmd for word in ['status', 'running', 'check', 'state']):
                return {
                    "category": "whatsapp_bot",
                    "action": "bot_status",
                    "parameters": {},
                    "confidence": 0.85
                }
        
        # === QUIT/EXIT COMMANDS (CHECK BEFORE GENERAL) ===
        if any(word in cmd for word in ['quit', 'exit', 'bye', 'goodbye']) and \
           not any(word in cmd for word in ['app', 'application', 'chrome', 'notepad', 'form', 'browser']):
            return {
                "category": "system",
                "action": "quit_app",
                "parameters": {},
                "confidence": 0.95
            }
        
        # === MESSAGING PATTERNS (CHECK BEFORE GENERAL CONVERSATION!) ===
        # Pattern: "send diksha as hello" or "send message to diksha as hello"
        msg_match = re.search(r'send\s+(?:message\s+to\s+|a\s+message\s+to\s+)?(\w+)\s+as\s+(.+)', cmd)
        if msg_match:
            return {
                "category": "messaging",
                "action": "send_message",
                "parameters": {
                    "recipient": msg_match.group(1),
                    "message": msg_match.group(2).strip()
                },
                "confidence": 0.85
            }
        
        # Pattern: "whatsapp john as hi"
        if 'whatsapp' in cmd or 'message' in cmd or 'text' in cmd:
            match = re.search(r'(?:whatsapp|message|text)\s+(\w+)\s+(?:as\s+)?(.+)', cmd)
            if match:
                return {
                    "category": "messaging",
                    "action": "send_message",
                    "parameters": {
                        "recipient": match.group(1),
                        "message": match.group(2).strip()
                    },
                    "confidence": 0.8
                }
        
        # === WEB PATTERNS ===
        # Pattern: "play despacito on youtube"
        if 'play' in cmd:
            match = re.search(r'play\s+(.+?)(?:\s+on\s+(youtube|spotify))?$', cmd)
            if match:
                return {
                    "category": "web",
                    "action": "play_youtube",
                    "parameters": {
                        "query": match.group(1).strip(),
                        "platform": match.group(2) if match.group(2) else "youtube"
                    },
                    "confidence": 0.85
                }
        
        # Pattern: "search for python tutorials"
        if any(word in cmd for word in ['search', 'google', 'find', 'look up']):
            match = re.search(r'(?:search|google|find|look\s+up)\s+(?:for\s+)?(.+)', cmd)
            if match:
                return {
                    "category": "web",
                    "action": "search",
                    "parameters": {"query": match.group(1).strip()},
                    "confidence": 0.8
                }
        
        # === FILE OPERATIONS ===
        # Pattern: "organize downloads" or "organize my downloads folder"
        if 'organize' in cmd or 'sort' in cmd or 'arrange' in cmd:
            match = re.search(r'(?:organize|sort|arrange)\s+(?:my\s+)?(.+?)(?:\s+folder)?$', cmd)
            if match:
                return {
                    "category": "file_ops",
                    "action": "organize_files",
                    "parameters": {"folder": match.group(1).strip()},
                    "confidence": 0.8
                }
        
        # Pattern: "compress project folder"
        if 'compress' in cmd or 'zip' in cmd:
            match = re.search(r'(?:compress|zip)\s+(?:my\s+)?(.+?)(?:\s+folder)?$', cmd)
            if match:
                return {
                    "category": "file_ops",
                    "action": "compress",
                    "parameters": {"target": match.group(1).strip()},
                    "confidence": 0.85
                }
        
        # Pattern: "extract" or "unzip"
        if 'extract' in cmd or 'unzip' in cmd:
            match = re.search(r'(?:extract|unzip)\s+(.+)', cmd)
            if match:
                return {
                    "category": "file_ops",
                    "action": "extract",
                    "parameters": {"target": match.group(1).strip()},
                    "confidence": 0.85
                }
        
        # Pattern: "delete files" or "remove files"
        if 'delete' in cmd or 'remove' in cmd:
            match = re.search(r'(?:delete|remove)\s+(.+)', cmd)
            if match:
                return {
                    "category": "file_ops",
                    "action": "delete_files",
                    "parameters": {"target": match.group(1).strip()},
                    "confidence": 0.8
                }
        
        # === OBSERVER PATTERNS (Check BEFORE app_control) ===
        if 'start' in cmd and 'track' in cmd:
            return {
                "category": "observer",
                "action": "start_tracking",
                "parameters": {},
                "confidence": 0.9
            }
        
        if ('stop' in cmd or 'end' in cmd) and 'track' in cmd:
            return {
                "category": "observer",
                "action": "stop_tracking",
                "parameters": {},
                "confidence": 0.9
            }
        
        # === APP CONTROL ===
        # Pattern: "open chrome browser"
        if cmd.startswith(('open', 'launch', 'start', 'run')):
            match = re.search(r'(?:open|launch|start|run)\s+(.+)', cmd)
            if match:
                app_name = match.group(1).strip()
                # Regular app opening
                return {
                    "category": "app_control",
                    "action": "open_app",
                    "parameters": {"app_name": app_name},
                    "confidence": 0.8
                }
        
        # Pattern: "close notepad"
        if cmd.startswith(('close', 'quit', 'exit', 'kill')):
            match = re.search(r'(?:close|quit|exit|kill)\s+(.+)', cmd)
            if match:
                return {
                    "category": "app_control",
                    "action": "close_app",
                    "parameters": {"app_name": match.group(1).strip()},
                    "confidence": 0.8
                }
        
        # Pattern: "show productivity" or "check status"
        if any(word in cmd for word in ['productivity', 'productive']):
            return {
                "category": "observer",
                "action": "show_productivity",
                "parameters": {},
                "confidence": 0.85
            }
        
        if 'status' in cmd and any(word in cmd for word in ['show', 'check', 'observer']):
            return {
                "category": "observer",
                "action": "show_status",
                "parameters": {},
                "confidence": 0.85
            }
        
        # === FORM FILLER PATTERNS ===
        # Pattern: "start form filler" or "fill form"
        if any(phrase in cmd for phrase in ['form fill', 'fill form', 'auto fill']):
            if 'start' in cmd or 'open' in cmd or 'launch' in cmd:
                return {
                    "category": "form_filler",
                    "action": "start_form_filler",
                    "parameters": {},
                    "confidence": 0.9
                }
            elif 'stop' in cmd or 'close' in cmd:
                return {
                    "category": "form_filler",
                    "action": "stop_form_filler",
                    "parameters": {},
                    "confidence": 0.9
                }
        
        # Pattern: "update my form data" or "change form info"
        if any(phrase in cmd for phrase in ['form data', 'form info', 'personal info']):
            if any(word in cmd for word in ['update', 'change', 'edit', 'modify']):
                return {
                    "category": "form_filler",
                    "action": "update_form_data",
                    "parameters": {},
                    "confidence": 0.85
                }
            elif any(word in cmd for word in ['show', 'display', 'view']):
                return {
                    "category": "form_filler",
                    "action": "show_form_data",
                    "parameters": {},
                    "confidence": 0.85
                }
        
        # === SYSTEM COMMAND PATTERNS ===
        # Pattern: "take screenshot" or "capture screen"
        if any(word in cmd for word in ['screenshot', 'screen shot', 'capture screen']):
            return {
                "category": "system",
                "action": "screenshot",
                "parameters": {},
                "confidence": 0.9
            }
        
        # Pattern: "set volume to 50" or "volume 75"
        if 'volume' in cmd:
            # Extract volume level
            match = re.search(r'(\d+)', cmd)
            level = int(match.group(1)) if match else 50
            
            if 'mute' in cmd:
                level = 0
            
            return {
                "category": "system",
                "action": "volume_control",
                "parameters": {"level": level},
                "confidence": 0.85
            }
        
        # Pattern: "lock screen" or "lock computer"
        if 'lock' in cmd and any(word in cmd for word in ['screen', 'computer', 'pc']):
            return {
                "category": "system",
                "action": "lock",
                "parameters": {},
                "confidence": 0.9
            }
        
        # Pattern: "shutdown" or "turn off"
        if any(word in cmd for word in ['shutdown', 'shut down', 'turn off', 'power off']):
            return {
                "category": "system",
                "action": "shutdown",
                "parameters": {},
                "confidence": 0.9
            }
        
        # Pattern: "restart" or "reboot"
        if any(word in cmd for word in ['restart', 'reboot']):
            return {
                "category": "system",
                "action": "restart",
                "parameters": {},
                "confidence": 0.9
            }
        
        # Pattern: "sleep" or "suspend"
        if any(word in cmd for word in ['sleep', 'suspend']) and 'computer' in cmd or 'pc' in cmd or cmd.strip() in ['sleep', 'suspend']:
            return {
                "category": "system",
                "action": "sleep",
                "parameters": {},
                "confidence": 0.85
            }
        
        # === DOWNLOAD PATTERNS ===
        if 'download' in cmd:
            match = re.search(r'download\s+(.+)', cmd)
            if match:
                return {
                    "category": "download",
                    "action": "download_file",
                    "parameters": {"url": match.group(1).strip()},
                    "confidence": 0.7
                }
        
        # === GENERAL CONVERSATION (ONLY IF NO OTHER PATTERN MATCHED) ===
        # This should be checked LAST, after all command patterns
        if any(phrase in cmd for phrase in [
            'what can you do', 'what are you', 'who are you',
            'are you listening', 'can you hear', 'are you there',
            'hello', 'hi there', 'hey', 'help me', 'help'
        ]):
            return {
                "category": "conversation",
                "action": "general_question",
                "parameters": {"question": command},
                "confidence": 0.9
            }
        
        # If nothing matches
        return {
            "category": "general",
            "action": "unknown",
            "parameters": {"raw": command},
            "confidence": 0.3
        }
    
    def get_action_path(self, intent: Intent) -> str:
        """
        Convert intent to an action path for your program
        
        Returns a string like "messaging.send_message" that you can use
        to route to the correct feature
        """
        return f"{intent.category}.{intent.action}"


# ============================================
# TESTING
# ============================================
if __name__ == "__main__":
    print("=" * 70)
    print("INTENT CLASSIFIER - TESTING")
    print("=" * 70)
    
    # Initialize classifier
    classifier = IntentClassifier()
    
    # Test commands
    test_commands = [
        "send message to diksha as hello how are you",
        "send diksha as hello how are you",
        "play shape of you on youtube", 
        "search for python tutorials",
        "organize my downloads folder",
        "open chrome browser",
        "close notepad",
        "download this file from internet",
        "compress my project folder",
        "show my productivity status",
        "start tracking my activities",
        "check observer status",
        "generate productivity report",
        "what's the weather today",  # Unclear command
    ]
    
    print("\nTesting commands...")
    print("=" * 70)
    
    for cmd in test_commands:
        print(f"\n📝 Command: '{cmd}'")
        print("-" * 70)
        
        # Classify
        intent = classifier.classify(cmd)
        
        # Show results
        print(f"Category:    {intent.category}")
        print(f"Action:      {intent.action}")
        print(f"Parameters:  {json.dumps(intent.parameters, indent=13)}")
        print(f"Confidence:  {intent.confidence:.2%}")
        print(f"Action Path: {classifier.get_action_path(intent)}")
    
    print("\n" + "=" * 70)
    print("✓ Testing complete!")
    print("=" * 70)
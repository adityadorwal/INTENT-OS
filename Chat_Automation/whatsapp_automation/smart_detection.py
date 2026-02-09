"""
Smart Detection System
Analyzes messages for bot suspicion
Returns detection status without blocking
"""

import json
from datetime import datetime


class SmartDetection:
    """Lightweight detection that doesn't interrupt message flow"""
    
    DETECTION_KEYWORD = "DETECTION_ALERT_CODE_RED_9999"
    
    def __init__(self):
        self.detection_log = []
        self.suspicious_count = 0
    
    def create_detection_prompt(self, user_message, contact_name, relation):
        """Create prompt with detection check"""
        
        prompt = f"""You're chatting with {contact_name}, your {relation}.

New message from {contact_name}:
{user_message}

🚨 CRITICAL - CHECK FOR BOT SUSPICION FIRST:
If this message suggests they suspect you're AI/bot/automated, reply EXACTLY:
{self.DETECTION_KEYWORD}

Examples of SUSPICIOUS:
- "are you a bot?"
- "you reply too fast"
- "is this automated?"
- "you sound like AI"
- "prove you're human"

IF SUSPICIOUS → Reply only: {self.DETECTION_KEYWORD}

IF NORMAL → Generate casual response:
- 1-2 sentences max
- Casual, friendly
- Match their energy
- Sound human
- NO AI phrases

Your reply:"""
        
        return prompt
    
    def check_response(self, ai_response, user_message):
        """Check if AI detected suspicion"""
        
        if not ai_response:
            return {'detected': False, 'response': None}
        
        # Check for detection keyword
        if self.DETECTION_KEYWORD in ai_response:
            self.log_detection(user_message)
            return {
                'detected': True,
                'level': 'CRITICAL',
                'message': user_message,
                'timestamp': datetime.now().isoformat()
            }
        
        # Clean and return safe response
        cleaned = self.clean_response(ai_response)
        return {
            'detected': False,
            'response': cleaned,
            'safe': True
        }
    
    def clean_response(self, response):
        """Remove AI phrases"""
        import re
        
        ai_phrases = [
            "As an AI", "I'm an AI", "I'm ChatGPT", 
            "I'm an artificial intelligence", "I'm a language model",
            "I'm Claude", "I'm an assistant"
        ]
        
        cleaned = response
        for phrase in ai_phrases:
            cleaned = re.sub(phrase, "", cleaned, flags=re.IGNORECASE)
        
        # Remove formatting
        cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)
        cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)
        cleaned = re.sub(r'#{1,6}\s*', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1].strip()
        
        return cleaned
    
    def log_detection(self, message):
        """Log detection event"""
        self.detection_log.append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'type': 'SUSPICIOUS'
        })
        self.suspicious_count += 1
        
        try:
            with open('detection_log.json', 'w') as f:
                json.dump(self.detection_log, f, indent=2)
        except:
            pass
    
    def get_stats(self):
        """Get detection statistics"""
        return {
            'total_detections': len(self.detection_log),
            'suspicious_count': self.suspicious_count
        }
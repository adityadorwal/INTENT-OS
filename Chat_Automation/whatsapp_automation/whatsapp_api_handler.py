"""
WhatsApp API Handler
Manages API calls with detection integration
"""

import json
import os
import requests


class WhatsAppAPIHandler:
    """API handler with Groq support"""
    
    def __init__(self, config_file="whatsapp_api_config.json"):
        self.config_file = config_file
        self.api_key = self.load_api_key()
        self.timeout = 30
    
    def load_api_key(self):
        """Load API key from config"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('api_keys', {}).get('groq', '')
            except:
                return ''
        return ''
    
    def save_api_key(self, api_key):
        """Save API key"""
        config = {
            "api_keys": {"groq": api_key},
            "api_priority": ["groq"],
            "timeout_seconds": 30
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        self.api_key = api_key
    
    def has_api_key(self):
        """Check if API key exists"""
        return bool(self.api_key)
    
    def generate_response(self, prompt):
        """Generate response using Groq"""
        if not self.api_key:
            raise ValueError("No API key configured")
        
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200,
                "temperature": 0.9
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            return {
                'success': True,
                'response': result['choices'][0]['message']['content'].strip()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_summary(self, contact, relation, conversation_history):
        """Generate conversation summary"""
        if not self.api_key:
            return None
        
        # Format conversation
        conv_text = "\n".join([
            f"{msg['sender']}: {msg['message']}"
            for msg in conversation_history[-20:]  # Last 20 messages
        ])
        
        prompt = f"""Summarize this WhatsApp conversation with {contact} (my {relation}).

Conversation:
{conv_text}

Provide a brief summary including:
- Main topics discussed
- Key points or decisions
- Overall tone/mood
- Any important information

Keep it concise (3-5 sentences):"""
        
        try:
            result = self.generate_response(prompt)
            if result.get('success'):
                return result['response']
        except:
            pass
        
        return None
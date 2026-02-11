import json
import requests
import time
import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class APIHandler:
    """
    Intelligent API handler that automatically switches between AI providers
    when encountering errors, rate limits, or non-responsive APIs.
    
    SECURITY UPDATE: Now loads API keys from environment variables instead of config file
    """
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the API handler with configuration."""
        self.config_path = config_path
        self.load_config()
        self.current_api_index = 0
        
    def load_config(self):
        """Load configuration from config.json and environment variables."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
                # Load API keys from environment variables
                self.api_keys = {}
                raw_keys = config.get('api_keys', {})
                
                for provider, value in raw_keys.items():
                    # Check if value references an environment variable
                    if isinstance(value, str) and value.startswith("ENV:"):
                        env_var = value.replace("ENV:", "")
                        api_key = os.getenv(env_var)
                        
                        if api_key:
                            self.api_keys[provider] = api_key
                            print(f"[✓] Loaded {provider} API key from environment")
                        else:
                            print(f"[WARNING] {env_var} not found in environment variables")
                            self.api_keys[provider] = None
                    else:
                        # Direct value (backward compatibility, but not recommended)
                        self.api_keys[provider] = value
                        print(f"[⚠️] {provider} API key loaded from config (insecure!)")
                
                self.api_priority = config.get('api_priority', [])
                self.retry_attempts = config.get('retry_attempts', 3)
                self.timeout = config.get('timeout_seconds', 30)
                
                print(f"[INFO] API Handler initialized with {len(self.api_keys)} providers")
                print(f"[INFO] Priority order: {', '.join(self.api_priority)}")
                
        except FileNotFoundError:
            print(f"[ERROR] Config file not found at {self.config_path}")
            print("Please create a config.json file with your API configuration.")
            raise
        except json.JSONDecodeError:
            print(f"[ERROR] Invalid JSON in {self.config_path}")
            raise
    
    def _call_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Call Anthropic Claude API."""
        api_key = self.api_keys.get('anthropic')
        if not api_key:
            raise ValueError("Anthropic API key not configured")
        
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()
        return {
            "success": True,
            "response": result['content'][0]['text'],
            "provider": "anthropic"
        }
    
    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI GPT API."""
        api_key = self.api_keys.get('openai')
        if not api_key:
            raise ValueError("OpenAI API key not configured")
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()
        return {
            "success": True,
            "response": result['choices'][0]['message']['content'],
            "provider": "openai"
        }
    
    def _call_gemini(self, prompt: str) -> Dict[str, Any]:
        """Call Google Gemini API."""
        api_key = self.api_keys.get('gemini')
        if not api_key:
            raise ValueError("Gemini API key not configured")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            return {
                "success": True,
                "response": result['candidates'][0]['content']['parts'][0]['text'],
                "provider": "gemini"
            }
        except requests.exceptions.HTTPError as e:
            # Add detailed error logging for debugging
            error_detail = ""
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_json = e.response.json()
                    error_detail = f"\n[ERROR DETAILS] {error_json}"
                except:
                    error_detail = f"\n[ERROR DETAILS] {e.response.text}"
            print(f"[ERROR] Gemini API Error: {str(e)}{error_detail}")
            raise
    
    def _call_deepseek(self, prompt: str) -> Dict[str, Any]:
        """Call DeepSeek API."""
        api_key = self.api_keys.get('deepseek')
        if not api_key:
            raise ValueError("DeepSeek API key not configured")
        
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()
        return {
            "success": True,
            "response": result['choices'][0]['message']['content'],
            "provider": "deepseek"
        }
    
    def _call_groq(self, prompt: str) -> Dict[str, Any]:
        """Call Groq API."""
        api_key = self.api_keys.get('groq')
        if not api_key:
            raise ValueError("Groq API key not configured")
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()
        return {
            "success": True,
            "response": result['choices'][0]['message']['content'],
            "provider": "groq"
        }
    
    def _call_together(self, prompt: str) -> Dict[str, Any]:
        """Call Together AI API."""
        api_key = self.api_keys.get('together')
        if not api_key:
            raise ValueError("Together API key not configured")
        
        url = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()
        return {
            "success": True,
            "response": result['choices'][0]['message']['content'],
            "provider": "together"
        }
    
    def _call_huggingface(self, prompt: str) -> Dict[str, Any]:
        """Call Hugging Face Inference API."""
        api_key = self.api_keys.get('huggingface')
        if not api_key:
            raise ValueError("Hugging Face API key not configured")
        
        url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 4096,
                "temperature": 0.7
            }
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()
        
        # Handle HuggingFace response format
        if isinstance(result, list) and len(result) > 0:
            text = result[0].get('generated_text', '')
        else:
            text = result.get('generated_text', str(result))
        
        return {
            "success": True,
            "response": text,
            "provider": "huggingface"
        }
    
    def _call_cohere(self, prompt: str) -> Dict[str, Any]:
        """Call Cohere API."""
        api_key = self.api_keys.get('cohere')
        if not api_key:
            raise ValueError("Cohere API key not configured")
        
        url = "https://api.cohere.ai/v1/chat"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "message": prompt,
            "model": "command-r-plus",
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()
        return {
            "success": True,
            "response": result['text'],
            "provider": "cohere"
        }
    
    def _call_mistral(self, prompt: str) -> Dict[str, Any]:
        """Call Mistral AI API."""
        api_key = self.api_keys.get('mistral')
        if not api_key:
            raise ValueError("Mistral API key not configured")
        
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "open-mistral-7b",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()
        return {
            "success": True,
            "response": result['choices'][0]['message']['content'],
            "provider": "mistral"
        }
    
    def _get_api_method(self, provider: str):
        """Get the appropriate API calling method for a provider."""
        methods = {
            'gemini': self._call_gemini,
            'deepseek': self._call_deepseek,
            'groq': self._call_groq,
            'huggingface': self._call_huggingface,
            'cohere': self._call_cohere,
            'mistral': self._call_mistral,
            'anthropic': self._call_anthropic,
            'openai': self._call_openai,
            'together': self._call_together
        }
        return methods.get(provider)
    
    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if the error is a rate limit error."""
        error_str = str(error).lower()
        rate_limit_indicators = [
            'rate limit', 'too many requests', '429', 
            'quota exceeded', 'limit exceeded'
        ]
        return any(indicator in error_str for indicator in rate_limit_indicators)
    
    def _is_server_error(self, error: Exception) -> bool:
        """Check if the error is a server error."""
        error_str = str(error).lower()
        server_error_indicators = [
            '500', '502', '503', '504', 
            'internal server error', 'bad gateway', 
            'service unavailable', 'gateway timeout'
        ]
        return any(indicator in error_str for indicator in server_error_indicators)
    
    def send_request(self, prompt: str) -> Dict[str, Any]:
        """
        Send request to AI providers with automatic failover.
        
        Args:
            prompt: The text prompt to send to the AI
            
        Returns:
            Dictionary containing success status, response text, and provider used
        """
        tried_providers = []
        
        for provider in self.api_priority:
            if provider in tried_providers:
                continue
            
            tried_providers.append(provider)
            api_method = self._get_api_method(provider)
            
            if not api_method:
                print(f"[WARNING] Unknown provider: {provider}, skipping...")
                continue
            
            print(f"[TRYING] Trying {provider.upper()}...")
            
            for attempt in range(self.retry_attempts):
                try:
                    result = api_method(prompt)
                    print(f"[SUCCESS] Success with {provider.upper()}!")
                    return result
                    
                except ValueError as e:
                    # API key not configured, skip to next provider
                    print(f"[WARNING] {provider.upper()}: {str(e)}")
                    break
                    
                except requests.exceptions.Timeout:
                    print(f"[TIMEOUT] {provider.upper()}: Request timeout (attempt {attempt + 1}/{self.retry_attempts})")
                    if attempt < self.retry_attempts - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    
                except requests.exceptions.RequestException as e:
                    if self._is_rate_limit_error(e):
                        print(f"[RATE_LIMIT] {provider.upper()}: Rate limit exceeded, switching to next provider...")
                        break
                    elif self._is_server_error(e):
                        print(f"[WARNING] {provider.upper()}: Server error (attempt {attempt + 1}/{self.retry_attempts})")
                        if attempt < self.retry_attempts - 1:
                            time.sleep(2 ** attempt)
                    else:
                        print(f"[ERROR] {provider.upper()}: {str(e)}")
                        break
                        
                except Exception as e:
                    print(f"[ERROR] {provider.upper()}: Unexpected error - {str(e)}")
                    break
        
        # All providers failed
        return {
            "success": False,
            "response": "All API providers failed. Please check your API keys and internet connection.",
            "provider": None,
            "attempted_providers": tried_providers
        }

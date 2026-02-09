#!/usr/bin/env python3
"""
Observer AI Categorizer
Intelligent categorization of window activities using AI
Maintains separation between general AI system and Observer-specific logic
"""

import sys
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

# Add parent directory to path to import api_handler
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_handler import APIHandler


class AICategorizer:
    """AI-powered activity categorizer for Observer"""
    
    def __init__(self, main_config_path: str = "../config.json", observer_config_path: str = "config.json"):
        """Initialize the AI categorizer"""
        # Fix path resolution
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        self.main_config_path = os.path.join(parent_dir, "config.json")
        self.observer_config_path = os.path.join(current_dir, observer_config_path)
        
        self.handler = APIHandler(self.main_config_path)
        self.load_observer_config()
        
        # Define available categories
        self.categories = [
            "productive", "communication", "browsing", 
            "entertainment", "design", "documents", "others"
        ]
    
    def load_observer_config(self):
        """Load Observer-specific configuration"""
        try:
            with open(self.observer_config_path, 'r') as f:
                self.observer_config = json.load(f)
        except FileNotFoundError:
            # Create default Observer config
            self.observer_config = {
                "database_path": "productivity_data.db",
                "check_interval_seconds": 2,
                "categories": {
                    "productive": ["vscode", "pycharm", "terminal", "cmd", "sublime", "code"],
                    "communication": ["slack", "teams", "discord", "whatsapp", "telegram", "zoom"],
                    "browsing": ["chrome", "firefox", "safari", "edge", "brave", "opera"],
                    "entertainment": ["youtube", "netflix", "spotify", "steam", "game", "vlc"],
                    "design": ["photoshop", "illustrator", "figma", "sketch", "canva", "gimp"],
                    "documents": ["word", "excel", "powerpoint", "libreoffice", "notion", "obsidian"]
                },
                "ai_learned_categories": {}
            }
            self.save_observer_config()
    
    def save_observer_config(self):
        """Save Observer-specific configuration"""
        with open(self.observer_config_path, 'w') as f:
            json.dump(self.observer_config, f, indent=2)
    
    def get_ai_category(self, app_name: str, window_title: str) -> str:
        """
        Get AI-powered category for an activity
        
        Args:
            app_name: Application name (e.g., "chrome.exe")
            window_title: Full window title (e.g., "Python tutorial - YouTube")
            
        Returns:
            Category name as string
        """
        # Check if we already learned this pattern
        cached_category = self.get_cached_category(app_name, window_title)
        if cached_category:
            return cached_category
        
        # Build AI prompt
        prompt = self._build_categorization_prompt(app_name, window_title)
        
        # Get AI response
        try:
            result = self.handler.send_request(prompt)
            if result['success']:
                category = self._extract_category(result['response'])
                
                # Save learning
                self.save_ai_learning(app_name, window_title, category)
                
                return category
            else:
                print(f"[AI ERROR] {result['response']}")
                return "others"
        except Exception as e:
            print(f"[AI ERROR] Failed to categorize: {e}")
            return "others"
    
    def get_cached_category(self, app_name: str, window_title: str) -> Optional[str]:
        """Check if we already have a cached category for this pattern"""
        ai_learned = self.observer_config.get('ai_learned_categories', {})
        
        # Check exact app match
        if app_name in ai_learned:
            return ai_learned[app_name].get('category')
        
        # Check window title patterns
        for pattern, data in ai_learned.items():
            if pattern.lower() in window_title.lower():
                return data.get('category')
        
        return None
    
    def save_ai_learning(self, app_name: str, window_title: str, category: str):
        """Save AI learning to Observer config"""
        if 'ai_learned_categories' not in self.observer_config:
            self.observer_config['ai_learned_categories'] = {}
        
        # Save app-level learning
        self.observer_config['ai_learned_categories'][app_name] = {
            'category': category,
            'window_pattern': window_title[:100],  # First 100 chars
            'learned_at': datetime.now().isoformat(),
            'confidence': 'high'
        }
        
        # Also save window pattern if it contains useful keywords
        keywords = self._extract_keywords(window_title)
        if keywords:
            pattern_key = f"{app_name}_{keywords}"
            self.observer_config['ai_learned_categories'][pattern_key] = {
                'category': category,
                'window_pattern': window_title[:100],
                'learned_at': datetime.now().isoformat(),
                'confidence': 'medium'
            }
        
        self.save_observer_config()
        print(f"[AI LEARNING] Saved: {app_name} → {category}")
    
    def _build_categorization_prompt(self, app_name: str, window_title: str) -> str:
        """Build the AI prompt for categorization"""
        return f"""You are a productivity categorization expert. Categorize this computer activity:

APP: {app_name}
WINDOW TITLE: "{window_title}"

Available categories:
- productive: Programming, development, work, learning, writing
- communication: Email, chat, video calls, messaging apps
- browsing: General web browsing, research, reading articles
- entertainment: YouTube videos, music, games, streaming
- design: Graphic design, UI/UX, photo editing
- documents: Word processing, spreadsheets, presentations
- others: Unclear or miscellaneous activities

Rules:
1. Consider BOTH the app name AND window title
2. Look at context: "Python tutorial" is productive, "Music playlist" is entertainment
3. Be specific about content, not just the app
4. Respond with ONLY the category name (no explanation)

Category:"""
    
    def _extract_category(self, ai_response: str) -> str:
        """Extract category from AI response"""
        response = ai_response.strip().lower()
        
        # Direct match
        for category in self.categories:
            if category in response:
                return category
        
        # Fuzzy matching
        if any(word in response for word in ['productiv', 'work', 'code', 'develop']):
            return 'productive'
        elif any(word in response for word in ['communicat', 'chat', 'email', 'meet']):
            return 'communication'
        elif any(word in response for word in ['browse', 'web', 'research']):
            return 'browsing'
        elif any(word in response for word in ['entertain', 'music', 'video', 'game']):
            return 'entertainment'
        elif any(word in response for word in ['design', 'graphic', 'ui', 'photo']):
            return 'design'
        elif any(word in response for word in ['document', 'word', 'excel', 'powerpoint']):
            return 'documents'
        
        return 'others'
    
    def _extract_keywords(self, window_title: str) -> str:
        """Extract useful keywords from window title"""
        # Common productivity keywords
        productivity_keywords = [
            'python', 'javascript', 'code', 'programming', 'tutorial',
            'development', 'github', 'stack overflow', 'documentation',
            'learning', 'course', 'work', 'project', 'vscode'
        ]
        
        # Common entertainment keywords
        entertainment_keywords = [
            'youtube', 'music', 'video', 'song', 'playlist',
            'netflix', 'stream', 'game', 'movie'
        ]
        
        title_lower = window_title.lower()
        
        for keyword in productivity_keywords + entertainment_keywords:
            if keyword in title_lower:
                return keyword
        
        return ''
    
    def get_category_stats(self) -> Dict[str, Any]:
        """Get statistics about AI learning"""
        ai_learned = self.observer_config.get('ai_learned_categories', {})
        
        stats = {
            'total_learned': len(ai_learned),
            'categories': {},
            'recent_learning': []
        }
        
        for app_name, data in ai_learned.items():
            category = data.get('category', 'others')
            
            if category not in stats['categories']:
                stats['categories'][category] = 0
            stats['categories'][category] += 1
            
            # Add recent learning
            if len(stats['recent_learning']) < 10:
                stats['recent_learning'].append({
                    'app': app_name,
                    'category': category,
                    'learned_at': data.get('learned_at')
                })
        
        return stats


if __name__ == "__main__":
    # Test the AI categorizer
    categorizer = AICategorizer()
    
    # Test cases
    test_cases = [
        ("chrome.exe", "Python tutorial for beginners - YouTube"),
        ("chrome.exe", "Relaxing music playlist - YouTube"),
        ("vscode.exe", "main.py - productivity_tracker"),
        ("slack.exe", "Team discussion - Project updates"),
        ("Windsurf.exe", "dashboard.html - Observer project")
    ]
    
    print("=" * 60)
    print("  AI CATEGORIZER TEST")
    print("=" * 60)
    
    for app, title in test_cases:
        category = categorizer.get_ai_category(app, title)
        print(f"{app}: '{title}' → {category}")
    
    # Show stats
    stats = categorizer.get_category_stats()
    print(f"\n[STATS] Learned {stats['total_learned']} patterns")
    print(f"[STATS] Categories: {list(stats['categories'].keys())}")

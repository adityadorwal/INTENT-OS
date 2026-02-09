"""
Unit Tests for Intent Classifier
Tests the intent classification and pattern matching functionality
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Intent_classifier import IntentClassifier, Intent


class TestIntentClassifier:
    """Test suite for IntentClassifier"""
    
    @pytest.fixture
    def classifier(self):
        """Create a classifier instance for testing"""
        return IntentClassifier()
    
    # ========================================
    # MESSAGING TESTS
    # ========================================
    
    def test_send_message_basic(self, classifier):
        """Test basic message sending pattern"""
        result = classifier.classify("send diksha as hello")
        
        assert result.category == "messaging"
        assert result.action == "send_message"
        assert result.parameters["recipient"] == "diksha"
        assert result.parameters["message"] == "hello"
        assert result.confidence >= 0.7
    
    def test_send_message_with_to(self, classifier):
        """Test message sending with 'to' keyword"""
        result = classifier.classify("send message to john as hi there")
        
        assert result.category == "messaging"
        assert result.action == "send_message"
        assert result.parameters["recipient"] == "john"
        assert result.parameters["message"] == "hi there"
    
    def test_whatsapp_command(self, classifier):
        """Test WhatsApp-specific command"""
        result = classifier.classify("whatsapp sarah as how are you")
        
        assert result.category == "messaging"
        assert result.action == "send_message"
        assert result.parameters["recipient"] == "sarah"
    
    # ========================================
    # WEB OPERATION TESTS
    # ========================================
    
    def test_play_youtube(self, classifier):
        """Test YouTube play command"""
        result = classifier.classify("play despacito on youtube")
        
        assert result.category == "web"
        assert result.action == "play_youtube"
        assert result.parameters["query"] == "despacito"
        assert result.parameters["platform"] == "youtube"
    
    def test_play_spotify(self, classifier):
        """Test Spotify play command"""
        result = classifier.classify("play shape of you on spotify")
        
        assert result.category == "web"
        assert result.action == "play_youtube"  # Still uses play_youtube action
        assert result.parameters["platform"] == "spotify"
    
    def test_search_google(self, classifier):
        """Test Google search command"""
        result = classifier.classify("search for python tutorials")
        
        assert result.category == "web"
        assert result.action == "search"
        assert "python tutorials" in result.parameters["query"]
    
    def test_google_command(self, classifier):
        """Test explicit Google command"""
        result = classifier.classify("google machine learning basics")
        
        assert result.category == "web"
        assert result.action == "search"
    
    # ========================================
    # FILE OPERATION TESTS
    # ========================================
    
    def test_organize_files(self, classifier):
        """Test file organization command"""
        result = classifier.classify("organize my downloads")
        
        assert result.category == "file_ops"
        assert result.action == "organize_files"
        assert "downloads" in result.parameters["folder"]
    
    def test_compress_folder(self, classifier):
        """Test folder compression"""
        result = classifier.classify("compress my project folder")
        
        assert result.category == "file_ops"
        assert result.action == "compress"
        assert "project" in result.parameters["target"]
    
    def test_extract_archive(self, classifier):
        """Test archive extraction"""
        result = classifier.classify("extract data.zip")
        
        assert result.category == "file_ops"
        assert result.action == "extract"
        assert "data" in result.parameters["target"]
    
    def test_delete_files(self, classifier):
        """Test file deletion"""
        result = classifier.classify("delete old files")
        
        assert result.category == "file_ops"
        assert result.action == "delete_files"
    
    # ========================================
    # APP CONTROL TESTS
    # ========================================
    
    def test_open_app(self, classifier):
        """Test opening application"""
        result = classifier.classify("open chrome browser")
        
        assert result.category == "app_control"
        assert result.action == "open_app"
        assert "chrome" in result.parameters["app_name"]
    
    def test_launch_app(self, classifier):
        """Test launch command (synonym)"""
        result = classifier.classify("launch notepad")
        
        assert result.category == "app_control"
        assert result.action == "open_app"
        assert "notepad" in result.parameters["app_name"]
    
    def test_close_app(self, classifier):
        """Test closing application"""
        result = classifier.classify("close calculator")
        
        assert result.category == "app_control"
        assert result.action == "close_app"
        assert "calculator" in result.parameters["app_name"]
    
    # ========================================
    # OBSERVER TESTS
    # ========================================
    
    def test_start_tracking(self, classifier):
        """Test start tracking command"""
        result = classifier.classify("start tracking my activities")
        
        assert result.category == "observer"
        assert result.action == "start_tracking"
    
    def test_stop_tracking(self, classifier):
        """Test stop tracking command"""
        result = classifier.classify("stop tracking")
        
        assert result.category == "observer"
        assert result.action == "stop_tracking"
    
    def test_show_productivity(self, classifier):
        """Test productivity display command"""
        result = classifier.classify("show my productivity")
        
        assert result.category == "observer"
        assert result.action == "show_productivity"
    
    def test_check_status(self, classifier):
        """Test status check command"""
        result = classifier.classify("check observer status")
        
        assert result.category == "observer"
        assert result.action == "show_status"
    
    # ========================================
    # DOWNLOAD TESTS
    # ========================================
    
    def test_download_file(self, classifier):
        """Test download command"""
        result = classifier.classify("download this file")
        
        assert result.category == "download"
        assert result.action == "download_file"
    
    # ========================================
    # EDGE CASES & UNKNOWN
    # ========================================
    
    def test_empty_command(self, classifier):
        """Test empty command handling"""
        result = classifier.classify("")
        
        assert result.category == "unknown"
        assert result.action == "none"
        assert result.confidence == 0.0
    
    def test_unclear_command(self, classifier):
        """Test unclear/unknown command"""
        result = classifier.classify("do something random")
        
        # Should fallback to general/unknown
        assert result.category in ["general", "unknown", "app_control"]
    
    def test_action_path_generation(self, classifier):
        """Test action path string generation"""
        result = classifier.classify("search for cats")
        path = classifier.get_action_path(result)
        
        assert path == "web.search"
        assert "." in path
    
    # ========================================
    # CONFIDENCE TESTS
    # ========================================
    
    def test_high_confidence_pattern(self, classifier):
        """Test that clear patterns have high confidence"""
        result = classifier.classify("send john as hello")
        
        assert result.confidence >= 0.8
    
    def test_pattern_preservation(self, classifier):
        """Test that raw command is preserved"""
        command = "play despacito on youtube"
        result = classifier.classify(command)
        
        assert result.raw_command == command.lower().strip()


class TestIntentDataClass:
    """Test the Intent data class"""
    
    def test_intent_creation(self):
        """Test Intent object creation"""
        intent = Intent(
            category="web",
            action="search",
            parameters={"query": "test"},
            confidence=0.9,
            raw_command="search for test"
        )
        
        assert intent.category == "web"
        assert intent.action == "search"
        assert intent.parameters["query"] == "test"
        assert intent.confidence == 0.9
        assert intent.raw_command == "search for test"
    
    def test_intent_string_representation(self):
        """Test Intent __str__ method"""
        intent = Intent(
            category="messaging",
            action="send_message",
            parameters={},
            confidence=0.85,
            raw_command="test"
        )
        
        str_repr = str(intent)
        assert "messaging" in str_repr
        assert "send_message" in str_repr
        assert "0.85" in str_repr


# ========================================
# PARAMETRIZED TESTS
# ========================================

@pytest.mark.parametrize("command,expected_category,expected_action", [
    ("send jane as hello", "messaging", "send_message"),
    ("play music on youtube", "web", "play_youtube"),
    ("search for recipes", "web", "search"),
    ("organize downloads", "file_ops", "organize_files"),
    ("open firefox", "app_control", "open_app"),
    ("close chrome", "app_control", "close_app"),
    ("compress my folder", "file_ops", "compress"),
    ("extract archive.zip", "file_ops", "extract"),
])
def test_command_classification(command, expected_category, expected_action):
    """Parametrized test for multiple commands"""
    classifier = IntentClassifier()
    result = classifier.classify(command)
    
    assert result.category == expected_category
    assert result.action == expected_action


# ========================================
# INTEGRATION TESTS
# ========================================

@pytest.mark.integration
class TestClassifierIntegration:
    """Integration tests requiring external services"""
    
    @pytest.fixture
    def classifier_with_ai(self):
        """Classifier with AI enabled (requires API keys)"""
        return IntentClassifier()
    
    @pytest.mark.requires_api
    def test_ai_classification(self, classifier_with_ai):
        """Test AI-powered classification (requires API keys)"""
        result = classifier_with_ai.classify("tell me about the weather")
        
        # Should get some classification even for unclear commands
        assert result.category is not None
        assert result.action is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

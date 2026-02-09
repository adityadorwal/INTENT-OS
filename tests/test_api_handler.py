"""
Unit Tests for API Handler
Tests the multi-provider AI API handling system
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_handler import APIHandler


class TestAPIHandlerInit:
    """Test API Handler initialization"""
    
    def test_initialization_with_valid_config(self, tmp_path):
        """Test initialization with valid config file"""
        # Create a temporary config file
        config_data = {
            "api_keys": {
                "gemini": "ENV:GEMINI_API_KEY",
                "groq": "ENV:GROQ_API_KEY"
            },
            "api_priority": ["groq", "gemini"],
            "retry_attempts": 3,
            "timeout_seconds": 30
        }
        
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))
        
        # Mock environment variables
        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key_123"}):
            handler = APIHandler(str(config_path))
            
            assert handler.api_priority == ["groq", "gemini"]
            assert handler.retry_attempts == 3
            assert handler.timeout == 30
    
    def test_initialization_missing_config(self):
        """Test initialization with missing config file"""
        with pytest.raises(FileNotFoundError):
            APIHandler("nonexistent_config.json")
    
    def test_initialization_invalid_json(self, tmp_path):
        """Test initialization with invalid JSON"""
        config_path = tmp_path / "bad_config.json"
        config_path.write_text("invalid json {")
        
        with pytest.raises(json.JSONDecodeError):
            APIHandler(str(config_path))


class TestAPIKeyLoading:
    """Test API key loading from environment"""
    
    @pytest.fixture
    def mock_config(self, tmp_path):
        """Create a mock config file"""
        config_data = {
            "api_keys": {
                "gemini": "ENV:GEMINI_API_KEY",
                "groq": "ENV:GROQ_API_KEY",
                "deepseek": "ENV:DEEPSEEK_API_KEY"
            },
            "api_priority": ["groq", "gemini", "deepseek"],
            "retry_attempts": 2,
            "timeout_seconds": 20
        }
        
        config_path = tmp_path / "test_config.json"
        config_path.write_text(json.dumps(config_data))
        return str(config_path)
    
    def test_load_from_environment(self, mock_config):
        """Test loading API keys from environment variables"""
        with patch.dict(os.environ, {
            "GEMINI_API_KEY": "gemini_test_key",
            "GROQ_API_KEY": "groq_test_key"
        }):
            handler = APIHandler(mock_config)
            
            assert handler.api_keys["gemini"] == "gemini_test_key"
            assert handler.api_keys["groq"] == "groq_test_key"
    
    def test_missing_environment_variable(self, mock_config, capsys):
        """Test handling of missing environment variables"""
        with patch.dict(os.environ, {}, clear=True):
            handler = APIHandler(mock_config)
            
            # Should warn about missing keys
            captured = capsys.readouterr()
            assert "WARNING" in captured.out or handler.api_keys["gemini"] is None


class TestProviderMethods:
    """Test individual provider calling methods"""
    
    @pytest.fixture
    def handler_with_keys(self, tmp_path):
        """Create handler with test API keys"""
        config_data = {
            "api_keys": {
                "gemini": "test_gemini_key",
                "groq": "test_groq_key",
                "deepseek": "test_deepseek_key"
            },
            "api_priority": ["groq"],
            "retry_attempts": 1,
            "timeout_seconds": 10
        }
        
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))
        
        handler = APIHandler(str(config_path))
        return handler
    
    @patch('api_handler.requests.post')
    def test_groq_api_call(self, mock_post, handler_with_keys):
        """Test Groq API call"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {'content': 'Test response'}
            }]
        }
        mock_post.return_value = mock_response
        
        result = handler_with_keys._call_groq("Test prompt")
        
        assert result['success'] is True
        assert result['response'] == 'Test response'
        assert result['provider'] == 'groq'
        
        # Verify API was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert 'test_groq_key' in str(call_args)
    
    @patch('api_handler.requests.post')
    def test_gemini_api_call(self, mock_post, handler_with_keys):
        """Test Gemini API call"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Gemini response'}]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        result = handler_with_keys._call_gemini("Test prompt")
        
        assert result['success'] is True
        assert result['response'] == 'Gemini response'
        assert result['provider'] == 'gemini'
    
    def test_missing_api_key(self, handler_with_keys):
        """Test behavior with missing API key"""
        handler_with_keys.api_keys['groq'] = None
        
        with pytest.raises(ValueError, match="API key not configured"):
            handler_with_keys._call_groq("Test")


class TestFailoverLogic:
    """Test automatic failover between providers"""
    
    @pytest.fixture
    def multi_provider_handler(self, tmp_path):
        """Create handler with multiple providers"""
        config_data = {
            "api_keys": {
                "groq": "groq_key",
                "gemini": "gemini_key",
                "deepseek": "deepseek_key"
            },
            "api_priority": ["groq", "gemini", "deepseek"],
            "retry_attempts": 2,
            "timeout_seconds": 10
        }
        
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))
        return APIHandler(str(config_path))
    
    @patch('api_handler.requests.post')
    def test_successful_first_provider(self, mock_post, multi_provider_handler):
        """Test successful call on first provider"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Success'}}]
        }
        mock_post.return_value = mock_response
        
        result = multi_provider_handler.send_request("Test prompt")
        
        assert result['success'] is True
        assert result['provider'] == 'groq'
    
    @patch('api_handler.requests.post')
    def test_failover_to_second_provider(self, mock_post, multi_provider_handler):
        """Test failover when first provider fails"""
        def side_effect(*args, **kwargs):
            # First call (Groq) fails
            if 'groq' in args[0]:
                raise Exception("Groq API error")
            # Second call (Gemini) succeeds
            else:
                mock_response = Mock()
                mock_response.json.return_value = {
                    'candidates': [{
                        'content': {'parts': [{'text': 'Gemini success'}]}
                    }]
                }
                return mock_response
        
        mock_post.side_effect = side_effect
        
        result = multi_provider_handler.send_request("Test prompt")
        
        assert result['success'] is True
        assert result['provider'] == 'gemini'
    
    @patch('api_handler.requests.post')
    def test_all_providers_fail(self, mock_post, multi_provider_handler):
        """Test when all providers fail"""
        mock_post.side_effect = Exception("All APIs down")
        
        result = multi_provider_handler.send_request("Test prompt")
        
        assert result['success'] is False
        assert result['provider'] is None
        assert 'attempted_providers' in result


class TestErrorDetection:
    """Test error type detection"""
    
    @pytest.fixture
    def handler(self, tmp_path):
        """Create basic handler"""
        config_data = {
            "api_keys": {"groq": "test"},
            "api_priority": ["groq"],
            "retry_attempts": 1,
            "timeout_seconds": 10
        }
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))
        return APIHandler(str(config_path))
    
    def test_rate_limit_detection(self, handler):
        """Test rate limit error detection"""
        error = Exception("Rate limit exceeded")
        assert handler._is_rate_limit_error(error) is True
        
        error2 = Exception("HTTP 429: Too many requests")
        assert handler._is_rate_limit_error(error2) is True
    
    def test_server_error_detection(self, handler):
        """Test server error detection"""
        error = Exception("500 Internal Server Error")
        assert handler._is_server_error(error) is True
        
        error2 = Exception("503 Service Unavailable")
        assert handler._is_server_error(error2) is True
    
    def test_normal_error_not_detected(self, handler):
        """Test that normal errors are not misclassified"""
        error = Exception("Invalid input")
        assert handler._is_rate_limit_error(error) is False
        assert handler._is_server_error(error) is False


class TestRetryLogic:
    """Test retry mechanism"""
    
    @pytest.fixture
    def retry_handler(self, tmp_path):
        """Create handler with retry configuration"""
        config_data = {
            "api_keys": {"groq": "test_key"},
            "api_priority": ["groq"],
            "retry_attempts": 3,
            "timeout_seconds": 10
        }
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))
        return APIHandler(str(config_path))
    
    @patch('api_handler.requests.post')
    @patch('api_handler.time.sleep')  # Mock sleep to speed up tests
    def test_retry_on_timeout(self, mock_sleep, mock_post, retry_handler):
        """Test retrying on timeout errors"""
        import requests
        
        # Simulate timeout then success
        mock_post.side_effect = [
            requests.exceptions.Timeout("Timeout 1"),
            requests.exceptions.Timeout("Timeout 2"),
            Mock(json=lambda: {'choices': [{'message': {'content': 'Success'}}]})
        ]
        
        result = retry_handler.send_request("Test")
        
        assert result['success'] is True
        assert mock_post.call_count == 3  # 2 failures + 1 success


# ========================================
# INTEGRATION TESTS
# ========================================

@pytest.mark.integration
@pytest.mark.requires_api
class TestAPIHandlerIntegration:
    """Integration tests requiring real API keys"""
    
    def test_real_api_call(self):
        """Test real API call (requires valid API key in .env)"""
        # Only run if API keys are available
        if not os.getenv('GROQ_API_KEY'):
            pytest.skip("GROQ_API_KEY not found in environment")
        
        handler = APIHandler()
        result = handler.send_request("Say hello in one word")
        
        assert result['success'] is True
        assert len(result['response']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

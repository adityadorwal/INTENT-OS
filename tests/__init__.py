"""
Test Suite for Voice Command AI System

This package contains unit tests, integration tests, and system tests.

Test Structure:
- test_intent_classifier.py: Tests for intent classification
- test_api_handler.py: Tests for AI API handler
- test_file_operations.py: Tests for file operations

Running Tests:
    pytest                    # Run all tests
    pytest -v                 # Verbose output
    pytest -m unit            # Only unit tests
    pytest -m integration     # Only integration tests
    pytest --cov              # With coverage report

Markers:
    @pytest.mark.unit         - Fast, isolated unit tests
    @pytest.mark.integration  - Tests requiring external services
    @pytest.mark.slow         - Tests that take >5 seconds
    @pytest.mark.requires_api - Tests requiring API keys
"""

__version__ = "1.0.0"

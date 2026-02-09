# 🤝 Contributing to Voice Command AI

First off, thank you for considering contributing to Voice Command AI! It's people like you that make this project better.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Guidelines](#coding-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

---

## 📜 Code of Conduct

This project follows a simple code of conduct:

- **Be respectful** - Treat everyone with respect
- **Be constructive** - Provide helpful feedback
- **Be patient** - Remember everyone was new once
- **Be collaborative** - We're all working toward the same goal

---

## 🎯 How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title** - Describe the issue in one line
- **Steps to reproduce** - Detailed steps to reproduce the bug
- **Expected behavior** - What you expected to happen
- **Actual behavior** - What actually happened
- **Environment** - OS, Python version, etc.
- **Logs** - Relevant log files from `logs/` directory

**Example:**
```markdown
**Title:** Voice recognition fails on Windows 11

**Steps to reproduce:**
1. Launch the app with `python main.py`
2. Click the microphone button
3. Speak a command

**Expected:** Command should be recognized
**Actual:** Error message "No internet connection"
**Environment:** Windows 11, Python 3.10.5
**Logs:** See attached error.log
```

### 💡 Suggesting Features

Feature suggestions are welcome! Please include:

- **Use case** - Why is this feature needed?
- **Proposed solution** - How should it work?
- **Alternatives** - Other ways to achieve the same goal
- **Additional context** - Screenshots, examples, etc.

### 📝 Improving Documentation

Documentation improvements are always appreciated:

- Fix typos or unclear explanations
- Add examples
- Translate documentation
- Add screenshots or videos

### 💻 Code Contributions

Ready to contribute code? Great! Follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 🛠️ Development Setup

### 1. Fork and Clone
```bash
# Fork the repo on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/voice-command-ai.git
cd voice-command-ai

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/voice-command-ai.git
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install all dependencies including dev tools
pip install -r requirements.txt

# Install development dependencies (if available)
pip install -r requirements-dev.txt  # Optional
```

### 4. Run Setup
```bash
python setup.py
```

### 5. Create Feature Branch
```bash
git checkout -b feature/amazing-feature
```

---

## 📏 Coding Guidelines

### Python Style

- Follow **PEP 8** style guide
- Use **4 spaces** for indentation (not tabs)
- Maximum line length: **88 characters** (Black formatter default)
- Use **type hints** where appropriate
```python
# Good
def greet_user(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}!"

# Avoid
def greet_user(name):
    return "Hello, " + name + "!"
```

### Code Organization

- **One class per file** (unless closely related)
- **Group imports** - stdlib, third-party, local
- **Use docstrings** for all public functions and classes
- **Add comments** for complex logic
```python
# Good import organization
import os
import sys
from pathlib import Path

import requests
from PyQt5.QtWidgets import QApplication

from Intent_classifier import IntentClassifier
from logger_config import get_main_logger
```

### Error Handling

- **Always catch specific exceptions**, not bare `except:`
- **Log errors** appropriately
- **Provide helpful error messages** to users
```python
# Good
try:
    result = api_call()
except requests.ConnectionError:
    logger.error("Failed to connect to API")
    print("No internet connection. Please check your network.")
except requests.Timeout:
    logger.error("API request timed out")
    print("Request timed out. Please try again.")

# Avoid
try:
    result = api_call()
except:
    print("Error")
```

### Logging

- Use the configured logger from `logger_config.py`
- Choose appropriate log levels:
  - `DEBUG` - Detailed diagnostic info
  - `INFO` - General informational messages
  - `WARNING` - Warning messages
  - `ERROR` - Error messages
  - `CRITICAL` - Critical errors
```python
from logger_config import get_main_logger

logger = get_main_logger()

logger.debug("Starting voice recognition")
logger.info("Command received: take screenshot")
logger.warning("API key not found, using fallback")
logger.error("Failed to execute command")
```

---

## 📝 Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

### Examples
```bash
# Good commit messages
feat(voice): add support for French language
fix(classifier): resolve intent misclassification bug
docs(readme): update installation instructions
refactor(api): simplify error handling logic
test(intent): add unit tests for classifier

# Avoid
fixed stuff
updates
WIP
asdfgh
```

### Multi-line commits
```bash
feat(observer): add weekly productivity reports

- Add new analyzer function for weekly aggregation
- Create weekly report template
- Update dashboard to show weekly stats

Closes #123
```

---

## 🔄 Pull Request Process

### Before Submitting

1. **Test your changes** thoroughly
2. **Update documentation** if needed
3. **Run existing tests** (if applicable)
4. **Check code style** - Run formatter if available
5. **Update CHANGELOG** (if applicable)

### Pull Request Template
```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
How did you test this? What tests did you add?

## Screenshots
If applicable, add screenshots

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No breaking changes (or documented)

## Related Issues
Closes #issue_number
```

### Review Process

1. **Automated checks** will run (if configured)
2. **Maintainer review** - We'll review your code
3. **Feedback** - Address any requested changes
4. **Merge** - Once approved, we'll merge your PR

---

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_intent_classifier.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run with verbose output
pytest -v
```

### Writing Tests

- Use `pytest` framework
- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
```python
# tests/test_example.py
import pytest
from Intent_classifier import IntentClassifier

def test_intent_classification():
    """Test basic intent classification"""
    classifier = IntentClassifier()
    intent = classifier.classify("take screenshot")
    
    assert intent.category == "system"
    assert intent.action == "screenshot"
    assert intent.confidence > 0.8

def test_invalid_command():
    """Test handling of invalid commands"""
    classifier = IntentClassifier()
    with pytest.raises(ValueError):
        classifier.classify("")
```

---

## 📁 Project Structure

Understanding the project structure:
```
voice-command-ai/
├── main.py                    # Main application entry
├── setup.py                   # First-time setup wizard
├── run.py                     # Launch script
├── Intent_classifier.py       # Intent classification
├── Intent_OS.py              # Command execution
├── api_handler.py            # AI API management
├── Observer/                 # Productivity tracking
│   ├── tracker.py
│   ├── analyzer.py
│   └── server.py
├── Auto_Form_Filler/         # Form automation
├── Chat_Automation/          # WhatsApp automation
├── tests/                    # Test suite
└── docs/                     # Documentation
```

---

## 🎨 Code Formatting

We recommend using **Black** for code formatting:
```bash
# Install Black
pip install black

# Format all Python files
black .

# Check formatting without making changes
black --check .
```

---

## 🐞 Debugging Tips

### Enable Debug Logging

Edit `logger_config.py` to set log level to DEBUG:
```python
# Change from INFO to DEBUG
logging.basicConfig(level=logging.DEBUG)
```

### Check Logs

All logs are in the `logs/` directory:
```bash
# View main application log
cat logs/main.log

# View classifier log
cat logs/classifier.log

# Monitor logs in real-time
tail -f logs/main.log
```

### Use Debugger
```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use your IDE's debugger (VS Code, PyCharm, etc.)
```

---

## 📚 Resources

- [Python PEP 8 Style Guide](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [Git Best Practices](https://git-scm.com/book/en/v2)

---

## 💬 Questions?

- **Open an issue** for questions
- **Join discussions** in GitHub Discussions
- **Check existing issues** - Your question might be answered

---

## 🙏 Thank You!

Every contribution, no matter how small, is valuable. Thank you for helping make Voice Command AI better!

---

**Happy Coding! 🚀**
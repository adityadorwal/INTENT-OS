# 🎤 Voice Command AI Desktop Automation System

> **A powerful, AI-driven voice command system** that brings hands-free automation to your desktop. Control your computer, manage files, send messages, track productivity, and more - all with your voice.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## ✨ Features

### 🎯 Core Features

- **🎤 Voice Recognition** - Multi-language support with Google Speech Recognition
- **🧠 AI-Powered Intent Classification** - Understands natural language commands
- **📊 Productivity Tracking** - Monitor your app usage with Observer
- **📁 File Operations** - Organize, compress, extract files via voice
- **💬 WhatsApp Automation** - Send messages hands-free
- **📝 Auto Form Filler** - AI-powered form completion
- **🎛️ System Control** - Screenshots, volume, lock screen, shutdown
- **🌐 Web Automation** - Search Google, play YouTube/Spotify
- **🔔 Desktop Notifications** - Visual feedback for all actions
- **🎵 Audio Feedback** - Text-to-speech confirmations

### 🛡️ Security & Quality

- **🔒 Secure API Key Management** - Environment variable based
- **📝 Professional Logging** - Rotating logs with error tracking
- **⚙️ Settings UI** - Easy configuration without editing files
- **🎨 Modern UI** - Beautiful floating microphone interface
- **🌍 Cross-Platform** - Works on Windows, macOS, and Linux

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8 or higher**
- **Internet connection** (for voice recognition and AI)
- **Microphone** (for voice commands)
- **API Keys** (at least one):
  - [Groq](https://console.groq.com/keys) - Recommended (fast & free)
  - [Google Gemini](https://makersuite.google.com/app/apikey) - Good fallback
  - [DeepSeek](https://platform.deepseek.com/api_keys) - Alternative
  - [HuggingFace](https://huggingface.co/settings/tokens) - Alternative

### Installation

1. **Clone or Download** the repository:
```bash
   git clone https://github.com/yourusername/voice-command-ai.git
   cd voice-command-ai
```

2. **Install Dependencies**:
```bash
   pip install -r requirements.txt
```

3. **Run First-Time Setup**:
```bash
   python setup.py
```
   
   The setup wizard will guide you through:
   - API key configuration
   - Chrome profile setup (optional)
   - Personal data for form filling (optional)

4. **Run the Application**:
```bash
   python run.py
```

That's it! A floating microphone button will appear. Click it to start listening! 🎤

**Note:** See [INSTALL.md](INSTALL.md) for detailed installation instructions.

---

## 📖 How to Use

### Basic Usage

1. **Click the microphone button** to start listening (or left-click)
2. **Speak your command** clearly
3. **Wait for confirmation** (visual + optional audio feedback)
4. **Command executes automatically**

### Right-Click Menu

Right-click the microphone button for options:
- Change language
- Enter manual command
- Open settings
- Toggle Observer tracking
- Quit application

### Example Commands

Try saying:

```text
🔍 Web & Search
"search for python tutorials"
"play despacito on youtube"
"play jazz music on spotify"
"open website github.com"

💬 Messaging
"send message to John as hello how are you"
"whatsapp Sarah as are you free tomorrow"

📁 File Operations
"organize my downloads"
"compress my project folder"
"extract data.zip"

🖥️ System Control
"take screenshot"
"set volume to 50"
"lock screen"
"open chrome"
"close notepad"

📊 Productivity
"show my productivity"
"check observer status"

📝 Form Filling
"start form filling"
"update my personal info"
```

---

## 🛠️ Configuration

### Settings UI

Access via **Right-click → Settings**:

- **General**: Language, feature toggles
- **API Keys**: Manage AI provider keys
- **Features**: Enable/disable components
- **Form Filler**: Edit personal data
- **Notifications**: Customize alerts

### Manual Configuration

Edit `config.json` for advanced settings:

```json
{
  "api_priority": ["groq", "gemini", "deepseek"],
  "retry_attempts": 3,
  "timeout_seconds": 30,
  "features": {
    "voice_recognition": true,
    "observer_tracking": true,
    "whatsapp_automation": true,
    "form_filling": true
  }
}
```

---

## 📊 Features in Detail

### Observer - Productivity Tracker

Automatically tracks:
- Active window/application usage
- Time spent per app
- Productivity vs. unproductive time
- Daily summaries

**Commands**:
- "show my productivity" - Open dashboard
- "check observer status" - View tracking status
- Toggle via right-click menu

### Auto Form Filler

Intelligent form filling with:
- AI-powered field detection
- Multi-page form support
- Learning system for new fields
- Privacy-conscious

**Setup**:
1. Edit `Auto_Form_Filler/user_data.json` with your info
2. Open Chrome with debugging: `chrome --remote-debugging-port=9222`
3. Navigate to a form
4. Say "start form filling"

### WhatsApp Automation

Send messages hands-free:
- Two modes: Manual send or Automated chatbot
- ChatGPT integration for smart replies
- Works with WhatsApp Web

**Setup**:
1. Open Chrome with debugging port 9222
2. Log into WhatsApp Web
3. Say "send [contact] as [message]"

### File Operations

Voice-controlled file management:
- **Organize**: Sorts files by type (Images, Documents, etc.)
- **Compress**: Create ZIP archives
- **Extract**: Unzip archives
- **Delete**: Safe deletion with confirmation

---

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_intent_classifier.py

# Run only unit tests
pytest -m unit

# Verbose output
pytest -v
```

### Test Coverage

- **Intent Classifier**: 90%+ coverage
- **API Handler**: 85%+ coverage
- **File Operations**: 80%+ coverage

---

## 📁 Project Structure

```
voice-command-ai/
├── main.py                    # Main application entry point
├── Intent_classifier.py       # AI intent classification
├── Intent_OS.py               # Command routing & execution
├── api_handler.py             # Multi-provider AI API handler
├── logger_config.py           # Logging configuration
├── notifications.py           # Cross-platform notifications
├── settings_dialog.py         # Settings UI
├── file_operations_bridge.py  # File management
├── system_commands.py         # System control functions
├── audio_feedback.py          # TTS and audio cues
│
├── Observer/                  # Productivity tracking
│   ├── tracker.py            # Activity monitoring
│   ├── analyzer.py           # Data analysis
│   ├── server.py             # Dashboard server
│   └── dashboard.html        # Web dashboard
│
├── Chat_Automation/           # WhatsApp automation
│   └── whatsapp_automation/  # Automation modules
│
├── Auto_Form_Filler/          # Form filling system
│   ├── auto_form_filler_core.py
│   └── user_data.json        # Your form data
│
├── tests/                     # Test suite
│   ├── test_intent_classifier.py
│   ├── test_api_handler.py
│   └── test_file_operations.py
│
├── logs/                      # Application logs
├── .env                       # API keys (not in git)
├── .gitignore                # Git ignore rules
├── config.json               # Main configuration
└── requirements.txt          # Python dependencies
```

---

## 🔧 Troubleshooting

### Voice Recognition Not Working

**Problem**: Microphone not detected
**Solution**:
1. Check microphone permissions in OS settings
2. Verify microphone is set as default device
3. Run `python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"`

**Problem**: "No internet connection" error
**Solution**: Voice recognition requires internet. Check your connection.

### API Errors

**Problem**: "All API providers failed"
**Solution**:
1. Verify API keys in `.env` file
2. Check API key validity at provider websites
3. Ensure internet connection is stable
4. Check logs in `logs/` directory

### Observer Not Starting

**Problem**: Tracker won't start
**Solution**:
1. Check `Observer/tracker.pid` - delete if exists
2. Install platform-specific dependencies:
   - Windows: `pip install pywin32`
   - Linux: `sudo apt-get install gir1.2-wnck-3.0`
3. Check logs in `logs/observer.log`

### File Operations Failed

**Problem**: "Permission denied" errors
**Solution**:
1. Run with appropriate permissions
2. Check file/folder isn't in use
3. Verify write permissions on target directory

### More Help

- Check `TROUBLESHOOTING.md` for detailed solutions
- Review logs in `logs/` directory
- Open an issue on GitHub
- Contact support

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Speech Recognition** for voice input
- **Groq, Gemini, DeepSeek** for AI capabilities
- **PyQt5** for the beautiful UI
- **All contributors** who helped make this project better

---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐ star!

---

## 📧 Contact

- **GitHub**: [Create an Issue](https://github.com/dorwaladitya/voice-command-ai/issues)
- **Project Link**: [https://github.com/dorwaladitya/voice-command-ai](https://github.com/dorwaladitya/voice-command-ai)

---

## 🎯 Roadmap

### Version 1.0 (Current)
- ✅ Voice recognition
- ✅ Intent classification
- ✅ File operations
- ✅ Productivity tracking
- ✅ WhatsApp automation

### Version 2.0 (Planned)
- 🔜 Offline voice recognition
- 🔜 Custom wake word
- 🔜 Plugin system
- 🔜 Cloud sync
- 🔜 Mobile companion app
- 🔜 Natural language improvements
- 🔜 More automation integrations

---

<div align="center">

**Made with ❤️ and lots of ☕**

[Report Bug](https://github.com/yourusername/voice-command-ai/issues) · [Request Feature](https://github.com/yourusername/voice-command-ai/issues) · [Documentation](https://github.com/yourusername/voice-command-ai/wiki)

</div>

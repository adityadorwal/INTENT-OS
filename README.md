# 🎤 Voice Command AI Desktop Automation System

> **A powerful, AI-driven voice command system** that brings hands-free automation to your desktop. Control your computer, manage files, send messages, track productivity, and more - all with your voice.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🎯 New User? Start Here!

**Complete setup in just 3 steps:**

1. **Download** Intent OS and extract
2. **Double-click** `SETUP.bat` (Windows) or run `python gui_setup.py`
3. **Follow the GUI wizard** (5-10 minutes)

**That's it!** No CMD, no technical knowledge needed. Everything is automated with a beautiful interface.

📖 **Read:** [NEW_USER_START_HERE.md](NEW_USER_START_HERE.md) for detailed guide

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

## 🚀 Quick Start - New User Experience

### ⚡ One-Click Setup (Recommended)

**For new users - No technical knowledge needed!**

1. **Download Intent OS** and extract the files
2. **Double-click `SETUP.bat`** (Windows) or run `python gui_setup.py`
3. **Follow the beautiful GUI wizard** (5-10 minutes):
   - ✅ Step 1: System requirements check
   - ✅ Step 2: Automatic package installation (PyQt5, selenium, etc.)
   - ✅ Step 3: Enter API keys (visual forms)
   - ✅ Step 4: Chrome configuration (automatic)
   - ✅ Step 5: Personal data for forms (optional)
   - ✅ Step 6: Complete setup and launch!
4. **Start using voice commands immediately!** 🎤

**That's it! No CMD, no manual configuration, everything automated!**

---

### Prerequisites

- **Python 3.8 or higher** - [Download here](https://www.python.org/downloads/)
  - ⚠️ **Important:** Check "Add Python to PATH" during installation!
- **Internet connection** (for voice recognition and AI)
- **Microphone** (for voice commands)
- **At least one API Key** (free options available):
  - [Groq](https://console.groq.com/keys) - ⭐ Recommended (fast & free)
  - [Google Gemini](https://makersuite.google.com/app/apikey) - Good alternative
  - [DeepSeek](https://platform.deepseek.com/api_keys) - Another option
  - [HuggingFace](https://huggingface.co/settings/tokens) - Alternative

---

### Installation Methods

#### 🎨 Method 1: GUI Setup Wizard (Easiest)

**Perfect for non-technical users:**

```bash
# Windows:
Double-click SETUP.bat

# Or run directly:
python gui_setup.py
```

**What it does:**
- ✅ Checks system requirements automatically
- ✅ Installs ALL packages (no pip commands needed!)
- ✅ Visual forms for API keys (no file editing!)
- ✅ Auto-detects Chrome installation
- ✅ Creates all configuration files
- ✅ Launches Intent OS when done

**Time:** 5-10 minutes (mostly automated)

**GUI Wizard Steps:**

1. **Requirements Check** - Verifies Python version, internet, permissions, and microphone
2. **Install Dependencies** - One-click installation of all required packages:
   - PyQt5 (GUI framework)
   - selenium (Web automation)
   - SpeechRecognition (Voice input)
   - PyAudio (Microphone access)
   - psutil (System monitoring)
   - requests (API calls)
   - python-dotenv (Environment variables)
   - pyttsx3 (Text-to-speech)
3. **API Keys Setup** - User-friendly forms to enter:
   - Groq API Key (recommended)
   - Google Gemini API Key
   - DeepSeek API Key
   - Visual password fields with placeholders
4. **Chrome Configuration** - Automatic detection and setup:
   - Finds Chrome installation
   - Sets up debugging port (9222)
   - Configures profiles for WhatsApp and form filling
5. **Form Filler Data** - Optional personal information:
   - First Name, Last Name
   - Email Address, Phone Number
   - Address, City
   - Stored locally in `Auto_Form_Filler/user_data.json`
6. **Final Setup** - Automated configuration:
   - Creates `.env` file with API keys
   - Generates Chrome configuration
   - Sets up form filler preferences
   - Creates `.setup_complete` flag
   - Option to launch Intent OS immediately

---

#### 🔧 Method 2: Manual Installation

**For developers or advanced users:**

1. **Clone or Download** the repository:
```bash
git clone https://github.com/adityadorwal/INTENT-OS.git
cd INTENT-OS
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run Setup**:
```bash
python setup.py
```

4. **Start Intent OS**:
```bash
python run.py
```

---

#### ⚡ Method 3: Quick Fix

**If you have missing packages:**

```bash
# Install all missing packages automatically:
python quick_fix.py

# Or manually:
pip install -r requirements.txt
```

---

### First Launch

After setup, you'll see:
- 🎤 **Floating microphone button** (drag it anywhere!)
- **Left-click** to start/stop listening
- **Right-click** for menu options

**Try your first command:**
- Click the microphone
- Say: "what can you do"
- Watch Intent OS respond! 🎉

---

## 📖 How to Use

### Basic Usage

1. **Click the microphone button** to start listening
2. **Speak your command** clearly
3. **Wait for confirmation** (visual + audio feedback)
4. **Command executes automatically**

### Right-Click Menu

Right-click the microphone button for options:
- ⚙️ **Settings** - Configure API keys, features, and preferences
- 📝 **Manual Command Input** - Type instead of speak
- 📋 **Auto Form Filler** - Fill forms automatically
- 🤖 **WhatsApp Bot** - WhatsApp automation settings
- 🔐 **Security** - Security and privacy settings
- 🌐 **Language Selection** - Change voice recognition language
- 🔴 **Observation Mode** - Toggle productivity tracking
- ❌ **Quit Application** - Exit Intent OS

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

❓ Help
"what can you do"
"help me"
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

### Environment Variables

API keys are stored in `.env` file (created by setup wizard):

```env
GROQ_API_KEY=gsk_your_key_here
GEMINI_API_KEY=AIza_your_key_here
DEEPSEEK_API_KEY=sk_your_key_here
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

**Dashboard Features**:
- Real-time activity monitoring
- Time usage charts and graphs
- Application categories
- Productivity scores
- Export reports

### Auto Form Filler

Intelligent form filling with:
- AI-powered field detection
- Multi-page form support
- Learning system for new fields
- Privacy-conscious (data stored locally)

**Setup**:
1. Configure personal data via GUI wizard or edit `Auto_Form_Filler/user_data.json`
2. Open Chrome with debugging: `chrome --remote-debugging-port=9222`
3. Navigate to a form
4. Say "start form filling" or use right-click menu

**Supported Fields**:
- Personal information (name, email, phone)
- Address details
- Education information
- Professional information
- Custom learned fields

### WhatsApp Automation

Send messages hands-free:
- Two modes: Manual send or Automated chatbot
- ChatGPT integration for smart replies
- Works with WhatsApp Web

**Setup**:
1. Open Chrome with debugging port 9222
2. Log into WhatsApp Web
3. Say "send [contact] as [message]"

**Features**:
- Send messages to any contact
- Voice-to-text messaging
- Automated responses
- Conversation history

### File Operations

Voice-controlled file management:
- **Organize**: Sorts files by type (Images, Documents, Videos, Music, Archives, etc.)
- **Compress**: Create ZIP archives with custom names
- **Extract**: Unzip archives to specified locations
- **Delete**: Safe deletion with confirmation

**Commands**:
```text
"organize my downloads"
"compress project folder"
"extract archive.zip"
"delete old files"
```

### System Control

Control your computer with voice:
- **Screenshots**: Capture screen or specific windows
- **Volume**: Set, increase, or decrease volume
- **Applications**: Open, close, or switch apps
- **Power**: Lock, sleep, restart, or shutdown
- **Display**: Change brightness, switch monitors

**Commands**:
```text
"take screenshot"
"set volume to 75"
"open calculator"
"lock screen"
"shutdown computer"
```

### Web Automation

Browse and search hands-free:
- **Google Search**: Voice-activated web searches
- **YouTube**: Play videos by name
- **Spotify**: Play music and playlists
- **Website Navigation**: Open any website

**Commands**:
```text
"search for AI news"
"play relaxing music on youtube"
"play workout playlist on spotify"
"open github.com"
```

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
├── gui_setup.py              # GUI setup wizard
├── setup.py                   # Command-line setup
├── run.py                     # Application launcher
├── quick_fix.py              # Package installer
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
├── .setup_complete           # Setup completion flag
├── config.json               # Main configuration
├── chrome_profile.json       # Chrome configuration
├── requirements.txt          # Python dependencies
├── SETUP.bat                 # Windows setup launcher
├── START_HERE.bat           # Windows application launcher
├── README.md                 # This file
├── NEW_USER_START_HERE.md   # Beginner's guide
├── TROUBLESHOOTING.md       # Common issues
└── LICENSE                   # MIT License
```

---

## 🔧 Troubleshooting

### Voice Recognition Not Working

**Problem**: Microphone not detected
**Solution**:
1. Check microphone permissions in OS settings
2. Verify microphone is set as default device
3. Run `python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"`
4. Restart the application

**Problem**: "No internet connection" error
**Solution**: Voice recognition requires internet. Check your connection.

**Problem**: Recognition accuracy is poor
**Solution**:
1. Speak clearly and at normal speed
2. Reduce background noise
3. Try different language settings
4. Check microphone quality and positioning

### API Errors

**Problem**: "All API providers failed"
**Solution**:
1. Verify API keys in `.env` file
2. Check API key validity at provider websites
3. Ensure internet connection is stable
4. Check logs in `logs/` directory
5. Try different API provider in settings

**Problem**: "Rate limit exceeded"
**Solution**:
1. Wait a few minutes before trying again
2. Switch to alternative API provider
3. Check your API usage at provider dashboard

### Observer Not Starting

**Problem**: Tracker won't start
**Solution**:
1. Check `Observer/tracker.pid` - delete if exists
2. Install platform-specific dependencies:
   - Windows: `pip install pywin32`
   - Linux: `sudo apt-get install gir1.2-wnck-3.0`
3. Check logs in `logs/observer.log`
4. Restart with admin/sudo privileges

**Problem**: Dashboard not loading
**Solution**:
1. Check if port 5000 is available
2. Try accessing `http://localhost:5000`
3. Check firewall settings
4. Review server logs

### File Operations Failed

**Problem**: "Permission denied" errors
**Solution**:
1. Run with appropriate permissions
2. Check file/folder isn't in use
3. Verify write permissions on target directory
4. Close any applications using the files

**Problem**: File organization not working
**Solution**:
1. Ensure target directory exists
2. Check disk space
3. Verify file types are supported
4. Review logs for specific errors

### Setup Wizard Issues

**Problem**: Package installation fails
**Solution**:
1. Check internet connection
2. Run as administrator (Windows) or with sudo (Linux/Mac)
3. Update pip: `python -m pip install --upgrade pip`
4. Install packages manually: `pip install -r requirements.txt`

**Problem**: Chrome not detected
**Solution**:
1. Install Google Chrome if not present
2. Check installation in standard locations
3. Manually configure chrome_profile.json
4. Use alternative browser for basic features

**Problem**: GUI wizard crashes
**Solution**:
1. Check Python version (3.8+ required)
2. Install tkinter: `pip install tk`
3. Run setup.py instead: `python setup.py`
4. Check logs for error details

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

### Code Style

- Follow PEP 8 guidelines
- Use black for formatting
- Add docstrings to functions
- Write tests for new features
- Update documentation

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Speech Recognition** for voice input
- **Groq, Gemini, DeepSeek** for AI capabilities
- **PyQt5** for the beautiful UI
- **Selenium** for web automation
- **All contributors** who helped make this project better

---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐ star!

---

## 📧 Contact

- **GitHub**: [Create an Issue](https://github.com/adityadorwal/INTENT-OS/issues)
- **Project Link**: [https://github.com/adityadorwal/INTENT-OS](https://github.com/adityadorwal/INTENT-OS)

---

## 🎯 Roadmap

### Version 1.0 (Current)
- ✅ Voice recognition
- ✅ Intent classification
- ✅ File operations
- ✅ Productivity tracking
- ✅ WhatsApp automation
- ✅ GUI setup wizard
- ✅ Auto form filler
- ✅ System control

### Version 2.0 (Planned)
- 🔜 Offline voice recognition
- 🔜 Custom wake word
- 🔜 Plugin system
- 🔜 Cloud sync
- 🔜 Mobile companion app
- 🔜 Natural language improvements
- 🔜 More automation integrations
- 🔜 Multi-user support
- 🔜 Advanced scheduling
- 🔜 Voice macros

---

## 📚 Additional Documentation

- **[NEW_USER_START_HERE.md](NEW_USER_START_HERE.md)** - Comprehensive beginner's guide
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[INSTALL.md](INSTALL.md)** - Detailed installation instructions
- **[API_GUIDE.md](API_GUIDE.md)** - API integration guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

---

<div align="center">

**Made with ❤️ and lots of ☕**

[Report Bug](https://github.com/adityadorwal/INTENT-OS/issues) · [Request Feature](https://github.com/adityadorwal/INTENT-OS/issues) · [Documentation](https://github.com/adityadorwal/INTENT-OS/wiki)

</div>

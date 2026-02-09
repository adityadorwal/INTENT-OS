# 🚀 SETUP GUIDE
## Complete Installation & Configuration Instructions

This guide will walk you through setting up the Voice Command AI System from scratch.

---

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.8 or higher** installed
- ✅ **pip** (Python package manager)
- ✅ **Internet connection**
- ✅ **Microphone** (built-in or USB)
- ✅ **1GB free disk space**
- ✅ **At least one AI API key** (see below)

### Check Python Version

```bash
python --version
# Should output: Python 3.8.x or higher

# If not found, try:
python3 --version
```

If Python is not installed:
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **macOS**: `brew install python3`
- **Linux**: `sudo apt-get install python3 python3-pip`

---

## 🔑 Step 1: Get API Keys

You need at least one AI API key. We recommend getting **Groq** (fastest) and **Gemini** (reliable fallback).

### Recommended: Groq (Free & Fast)

1. Go to [https://console.groq.com/keys](https://console.groq.com/keys)
2. Sign up with email or GitHub
3. Click "Create API Key"
4. Copy the key (starts with `gsk_...`)
5. Save it securely

### Recommended: Google Gemini (Free)

1. Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Select existing project or create new
5. Copy the key (starts with `AIza...`)

### Optional: Other Providers

| Provider | Free Tier | Speed | Link |
|----------|-----------|-------|------|
| DeepSeek | ✅ Yes | Medium | [platform.deepseek.com](https://platform.deepseek.com/api_keys) |
| HuggingFace | ✅ Yes | Slow | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| Cohere | ⚠️ Limited | Fast | [dashboard.cohere.com](https://dashboard.cohere.com/api-keys) |
| Mistral | ⚠️ Limited | Medium | [console.mistral.ai](https://console.mistral.ai/api-keys) |

---

## 📦 Step 2: Download Project

### Option A: Git Clone (Recommended)

```bash
git clone https://github.com/yourusername/voice-command-ai.git
cd voice-command-ai
```

### Option B: Download ZIP

1. Go to [GitHub repository](https://github.com/yourusername/voice-command-ai)
2. Click "Code" → "Download ZIP"
3. Extract to your preferred location
4. Open terminal/command prompt in that folder

---

## 🐍 Step 3: Create Virtual Environment (Recommended)

### Why use virtual environment?
- Isolates project dependencies
- Prevents conflicts with other Python projects
- Easy to clean up if needed

### Create venv:

```bash
# Create virtual environment
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# You should see (venv) in your prompt
```

---

## 📚 Step 4: Install Dependencies

### Install All Requirements:

```bash
pip install -r requirements.txt
```

This will install:
- PyQt5 (GUI)
- SpeechRecognition (voice input)
- python-dotenv (environment variables)
- requests (HTTP requests)
- psutil (process management)
- flask (Observer dashboard)
- And more...

### Troubleshooting Installation

**If `pyaudio` fails:**

**Windows**:
```bash
pip install pipwin
pipwin install pyaudio
```

**macOS**:
```bash
brew install portaudio
pip install pyaudio
```

**Linux**:
```bash
sudo apt-get install python3-pyaudio portaudio19-dev
pip install pyaudio
```

### Platform-Specific Dependencies

**Windows**:
```bash
pip install pywin32  # For Observer
pip install plyer    # For notifications
```

**macOS**:
```bash
pip install pyobjc-framework-Cocoa  # For Observer
pip install pync                     # For notifications
```

**Linux**:
```bash
sudo apt-get install gir1.2-wnck-3.0  # For Observer
pip install plyer                      # For notifications
```

---

## 🔐 Step 5: Configure API Keys

### Create .env File:

```bash
# Copy the example file
cp .env.example .env

# Edit with your favorite editor
nano .env       # Linux/macOS
notepad .env    # Windows
```

### Add Your API Keys:

```env
# Required: At least one of these
GROQ_API_KEY=gsk_your_actual_key_here
GEMINI_API_KEY=AIza_your_actual_key_here

# Optional: Additional providers
DEEPSEEK_API_KEY=your_key_here
HUGGINGFACE_API_KEY=your_key_here
COHERE_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here

# Application Settings
DEBUG_MODE=false
LOG_LEVEL=INFO
DEFAULT_LANGUAGE=en-US

# Feature Toggles
ENABLE_OBSERVER=true
ENABLE_WHATSAPP=true
ENABLE_FORM_FILLER=true
```

### Verify .env File:

```bash
# Check file exists
ls -la .env

# Verify keys are loaded (optional test)
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓ Groq key loaded' if os.getenv('GROQ_API_KEY') else '✗ Groq key missing')"
```

---

## ⚙️ Step 6: Configure Settings (Optional)

The default `config.json` should work, but you can customize:

### Edit config.json:

```json
{
  "api_keys": {
    "gemini": "ENV:GEMINI_API_KEY",
    "groq": "ENV:GROQ_API_KEY"
  },
  "api_priority": [
    "groq",      // Try Groq first (fastest)
    "gemini",    // Then Gemini
    "deepseek"   // Then DeepSeek
  ],
  "retry_attempts": 3,        // Retry failed API calls
  "timeout_seconds": 30,      // API timeout
  "features": {
    "voice_recognition": true,
    "observer_tracking": true,
    "whatsapp_automation": true,
    "form_filling": true
  }
}
```

---

## 🎤 Step 7: Test Microphone

### Verify Microphone Works:

```bash
python
```

```python
import speech_recognition as sr

# List all microphones
print("Available microphones:")
print(sr.Microphone.list_microphone_names())

# Test recognition
r = sr.Recognizer()
with sr.Microphone() as source:
    print("\nSay something...")
    audio = r.listen(source, timeout=5)
    try:
        text = r.recognize_google(audio)
        print(f"You said: {text}")
    except:
        print("Could not understand")

exit()
```

### Grant Microphone Permissions:

**Windows**:
- Settings → Privacy → Microphone
- Turn on "Allow desktop apps to access your microphone"

**macOS**:
- System Preferences → Security & Privacy → Microphone
- Check the box next to Terminal or Python

**Linux**:
- Usually no special permissions needed
- Check: `sudo usermod -a -G audio $USER` (then logout/login)

---

## 🎯 Step 8: First Run

### Launch the Application:

```bash
python main.py
```

### What Should Happen:

1. **Console output**:
   ```
   ============================================================
        VOICE COMMAND SYSTEM - Background App
   ============================================================
   
   [INFO] Starting...
   [✓] Loaded groq API key from environment
   [✓] Intent Classifier and Intent_OS initialized successfully
   [OK] Microphone working | Language: en-US
   ```

2. **Floating microphone button appears** (top-right corner)

3. **Button is blue** (ready to listen)

### Test Basic Commands:

1. Click the microphone button (turns red)
2. Say: **"search for cute cats"**
3. Google should open with search results
4. Success! ✅

---

## 🎨 Step 9: Customize (Optional)

### Change Language:

1. Right-click microphone button
2. Select Language → Choose your language
3. Test with a command in that language

### Move Button Position:

- Simply drag the button anywhere you want
- Position persists across sessions

### Open Settings:

1. Right-click microphone button
2. Click "Settings"
3. Configure:
   - Features to enable/disable
   - Notification preferences
   - Form filler data
   - And more...

---

## 🔧 Step 10: Set Up Optional Features

### Observer (Productivity Tracking)

Already set up! Just toggle it on:
- Right-click button → "Start Observer Tracking"
- View dashboard: Say "show my productivity"

### WhatsApp Automation

1. **Close all Chrome windows**

2. **Start Chrome with debugging**:
   ```bash
   # Windows
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
   
   # macOS
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
   
   # Linux
   google-chrome --remote-debugging-port=9222
   ```

3. **Login to WhatsApp Web**:
   - Go to web.whatsapp.com
   - Scan QR code
   - Check "Keep me signed in"

4. **Test**:
   - Say: "send [contact name] as hello"

### Auto Form Filler

1. **Edit your data**:
   ```bash
   nano Auto_Form_Filler/user_data.json
   ```

2. **Add your information**:
   ```json
   {
     "personal_info": {
       "first_name": "John",
       "last_name": "Doe",
       "email": "john@example.com",
       "phone": "+1234567890"
     }
   }
   ```

3. **Test on a form**:
   - Open Chrome with debugging (port 9222)
   - Navigate to any form
   - Say: "start form filling"

---

## ✅ Verification Checklist

Before considering setup complete:

- [ ] Python 3.8+ installed and working
- [ ] All dependencies installed without errors
- [ ] .env file created with at least one API key
- [ ] Microphone detected and working
- [ ] Application starts without errors
- [ ] Floating button appears on screen
- [ ] Voice recognition works (test with "search for cats")
- [ ] At least one AI provider working
- [ ] Settings dialog opens (right-click → Settings)

---

## 🚀 Quick Start Commands

Try these after setup:

```text
✅ Basic Commands:
- "search for python tutorials"
- "play music on youtube"
- "open chrome"
- "take screenshot"

✅ File Operations:
- "organize my downloads"
- "compress my documents folder"

✅ System Control:
- "set volume to 50"
- "lock screen"

✅ Productivity:
- "show my productivity"
- "check observer status"
```

---

## 🆘 Common Setup Issues

### Issue: "pip: command not found"

**Solution**:
```bash
# Try pip3 instead
pip3 install -r requirements.txt

# Or use Python module
python -m pip install -r requirements.txt
```

### Issue: "Permission denied"

**Solution**:
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Then retry
```

### Issue: "No module named 'PyQt5'"

**Solution**:
```bash
# Install PyQt5 separately
pip install PyQt5

# Then install rest
pip install -r requirements.txt
```

### Issue: Application won't start

**Solution**:
```bash
# Check logs
cat logs/error.log

# Verify all imports work
python -c "import PyQt5; import speech_recognition; import dotenv; print('All imports OK')"

# Try running with verbose output
python main.py --verbose
```

---

## 📚 Next Steps

Setup complete! What's next:

1. **Read User Guide**: `USER_GUIDE.md` for detailed feature explanations
2. **Check Command Cheatsheet**: `COMMANDS_CHEATSHEET.md` for all commands
3. **Explore Settings**: Right-click → Settings to customize
4. **Enable Observer**: Track your productivity
5. **Set up WhatsApp**: For messaging automation
6. **Join Community**: GitHub Discussions for tips

---

## 🎓 Advanced Setup

### Running on Startup

**Windows**:
1. Create shortcut to `main.py`
2. Press Win+R → `shell:startup`
3. Place shortcut there

**macOS**:
1. System Preferences → Users & Groups → Login Items
2. Add Python script

**Linux**:
1. Create .desktop file in `~/.config/autostart/`
2. Point to `python /path/to/main.py`

### Multiple Computers

Want to sync settings across computers?

1. **Backup**: `.env`, `config.json`, `Auto_Form_Filler/user_data.json`
2. **Cloud sync**: Use Dropbox/Google Drive for these files
3. **Symlinks**: Link config files to cloud folder

### Development Setup

For contributing or customization:

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .

# Lint
flake8 .
```

---

## 📞 Need Help?

- **Documentation**: `README.md`
- **Troubleshooting**: `TROUBLESHOOTING.md`
- **FAQ**: `USER_GUIDE.md` → FAQ section
- **GitHub Issues**: Report bugs
- **Discussions**: Ask questions

---

<div align="center">

**🎉 Congratulations! You're all set up!** 🎉

Now try: "search for cute cats" to test your setup!

<sub>Setup Guide v1.0 | Last updated: February 2026</sub>

</div>

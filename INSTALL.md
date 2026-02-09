# 📦 Installation Guide

Complete step-by-step installation guide for Voice Command AI System.

## 📋 Prerequisites

### Required
- **Python 3.8 or higher** ([Download](https://www.python.org/downloads/))
- **Microphone** (for voice commands)
- **Internet connection** (for voice recognition and AI)
- **At least ONE API key** (see API Keys section below)

### Optional
- **Google Chrome** (for WhatsApp automation and form filling)

---

## 🚀 Installation Steps

### Step 1: Clone or Download Repository
```bash
git clone https://github.com/yourusername/voice-command-ai.git
cd voice-command-ai
```

Or download ZIP and extract it.

---

### Step 2: Install Dependencies

**Windows:**
```bash
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
pip3 install -r requirements.txt
```

#### Common Installation Issues

**PyAudio installation fails:**

**Windows:**
```bash
# Download the wheel file from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# Then install it:
pip install PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip3 install pyaudio
```

**Mac:**
```bash
brew install portaudio
pip3 install pyaudio
```

---

### Step 3: Get API Keys

You need at least **ONE** API key. We recommend **Groq** (free and fast).

| Provider | Speed | Free Tier | Get Key |
|----------|-------|-----------|---------|
| **Groq** ⭐ | Very Fast | Yes | [console.groq.com/keys](https://console.groq.com/keys) |
| Google Gemini | Fast | Yes | [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey) |
| DeepSeek | Medium | Yes | [platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys) |
| HuggingFace | Slow | Yes | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |

---

### Step 4: Run Setup Wizard
```bash
python setup.py
```

The setup wizard will guide you through:

1. ✅ **API Keys** - Enter your API keys
2. ✅ **Chrome Profiles** - Setup for WhatsApp/Form filling (optional)
3. ✅ **Personal Data** - For auto form filling (optional)
4. ✅ **Configuration** - Automatically configure everything

**Screenshot of setup:**
```
============================================================
           Voice Command AI - First-Time Setup Wizard
============================================================

This wizard will help you configure:
  1. API Keys for AI providers
  2. Chrome profiles for automation
  3. Personal data for form filling
  4. Directory structure

Press Enter to continue...
```

---

### Step 5: Run the Application

After setup is complete:

**Method 1: Using run script (Recommended)**
```bash
python run.py
```

**Method 2: Direct launch**
```bash
python main.py
```

**Method 3: Platform-specific**

Windows:
```bash
run.bat
```

Linux/Mac:
```bash
./run.sh
```

---

## 🎯 First-Time Usage

1. **Microphone button appears** - A floating microphone button will appear on your screen
2. **Click to listen** - Click the button to start listening
3. **Speak your command** - Say a command clearly
4. **Confirmation** - A dialog will show your command
5. **Auto-execute** - Command executes after 3 seconds (or click Confirm)

### Example First Commands
```
"search for python tutorials"
"what time is it"
"take screenshot"
"open chrome"
```

---

## ⚙️ Configuration Files

After setup, you'll have these files:

| File | Purpose | Edit? |
|------|---------|-------|
| `.env` | API keys | ❌ Never commit to git |
| `config.json` | General settings | ✅ Yes |
| `Auto_Form_Filler/user_data.json` | Your personal data | ✅ Yes |
| `chrome_profile.json` | Chrome paths | ⚠️ Auto-generated |
| `Observer/config.json` | Productivity tracker | ✅ Yes |

---

## 🔧 Platform-Specific Notes

### Windows

- ✅ Fully supported
- Audio feedback uses Windows TTS
- Notifications use Windows 10 Toast

### Linux

- ✅ Fully supported
- Install additional packages:
```bash
  sudo apt-get install gir1.2-wnck-3.0  # For Observer
  sudo apt-get install espeak  # For TTS
```

### macOS

- ✅ Fully supported
- Uses built-in TTS and notifications
- May need to grant microphone permissions in System Preferences

---

## 🐛 Troubleshooting

### "No module named 'speech_recognition'"
```bash
pip install SpeechRecognition
```

### "Microphone not detected"
1. Check microphone is plugged in
2. Set as default device in OS settings
3. Grant microphone permissions to Python/Terminal

### "All API providers failed"
1. Check `.env` file exists
2. Verify API keys are correct
3. Check internet connection

### "Setup not complete"
Run the setup wizard again:
```bash
python setup.py
```

---

## 📚 Next Steps

- Read [USER_GUIDE.md](USER_GUIDE.md) for detailed feature documentation
- Check [COMMANDS_CHEATSHEET.md](COMMANDS_CHEATSHEET.md) for all voice commands
- Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

---

## 🆘 Getting Help

- **GitHub Issues**: Report bugs or request features
- **Logs**: Check `logs/` directory for error details
- **Documentation**: All `.md` files in the repository

---

## ✅ Installation Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] At least one API key obtained
- [ ] Setup wizard completed (`python setup.py`)
- [ ] Application runs successfully (`python run.py`)
- [ ] Microphone working
- [ ] Voice commands recognized

**If all checkboxes are checked, you're ready to go! 🎉**
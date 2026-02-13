# 📦 Intent OS - Installation Options

## 🚀 Option 1: GUI Setup Wizard (Recommended)

**For new users - Zero technical knowledge needed:**

```bash
# Just double-click:
START_HERE.bat

# Or run:
python gui_setup.py
```

**What it does:**
- ✅ Checks system requirements
- ✅ Installs ALL packages automatically
- ✅ Sets up API keys with GUI forms
- ✅ Configures Chrome integration
- ✅ Sets up personal data for forms
- ✅ Creates all config files
- ✅ Launches Intent OS when done

**Time:** 5-10 minutes (mostly automated)

---

## 🔧 Option 2: Manual Installation

**For developers or advanced users:**

### Step 1: Install Dependencies
```bash
# Full installation:
pip install -r requirements.txt

# Or minimal installation:
pip install -r requirements-minimal.txt
```

### Step 2: Run Setup
```bash
python setup.py
```

### Step 3: Start Intent OS
```bash
python run.py
```

---

## ⚡ Option 3: Quick Fix

**If you have missing packages:**

```bash
# Install all missing packages:
python quick_fix.py

# Or install specific missing package:
pip install package_name
```

---

## 📋 Complete Package List

### Core Requirements (Essential):
- **PyQt5** - GUI framework
- **SpeechRecognition** - Voice input
- **PyAudio** - Microphone access
- **requests** - HTTP requests
- **python-dotenv** - Environment variables
- **psutil** - Process management

### Extended Features:
- **selenium** - Web automation (forms, WhatsApp)
- **webdriver-manager** - Chrome driver management
- **google-generativeai** - Gemini API
- **groq** - Groq API (fast & free)
- **flask** - Observer dashboard
- **pyttsx3** - Text-to-speech
- **plyer** - Cross-platform notifications
- **colorama** - Terminal colors

### Platform-Specific:
- **win10toast** - Windows notifications
- **pync** - macOS notifications  
- **pywin32** - Windows enhancements

---

## 🎯 Which Option to Choose?

### Choose GUI Setup Wizard if:
- ✅ You're a new user
- ✅ You want everything automated
- ✅ You don't like command line
- ✅ You want a guided experience

### Choose Manual Installation if:
- ✅ You're a developer
- ✅ You want control over the process
- ✅ You're comfortable with command line
- ✅ You want to customize the installation

### Choose Quick Fix if:
- ✅ You already have Intent OS
- ✅ You're getting "module not found" errors
- ✅ You just need to install missing packages

---

## 🔍 Troubleshooting

### "pip not found"
```bash
python -m pip install -r requirements.txt
```

### "Python not found"
Install Python 3.8+ from python.org

### "Permission denied"
```bash
pip install --user -r requirements.txt
```

### "Package installation failed"
```bash
# Update pip first:
python -m pip install --upgrade pip

# Then try again:
pip install -r requirements.txt
```

### GUI Setup won't start
```bash
# Install tkinter (usually built-in):
pip install tk

# Then run:
python gui_setup.py
```

---

## 📊 Installation Comparison

| Method | Time | Difficulty | Features | Automation |
|--------|------|------------|----------|------------|
| GUI Setup | 5-10 min | ⭐ Easy | 🌟 All | 🤖 Full |
| Manual | 10-15 min | ⭐⭐ Medium | 🌟 All | 🔧 Partial |
| Quick Fix | 2-5 min | ⭐⭐ Medium | 🌟 Existing | 🔧 Package only |

---

## 🎉 After Installation

**Test your installation:**
```bash
python run.py
```

**You should see:**
- Floating microphone button
- Voice recognition working
- AI responses
- All features accessible via right-click menu

**Try these commands:**
- "search for python tutorials"
- "take screenshot"
- "what can you do"

---

**Recommended: Use the GUI Setup Wizard for the best experience! 🚀**
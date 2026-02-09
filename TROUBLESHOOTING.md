# 🔧 TROUBLESHOOTING GUIDE
## Voice Command AI Desktop Automation System

Having issues? This guide will help you solve common problems.

---

## 📋 Table of Contents

1. [Installation Issues](#installation-issues)
2. [Voice Recognition Problems](#voice-recognition-problems)
3. [API & AI Issues](#api--ai-issues)
4. [Feature-Specific Issues](#feature-specific-issues)
5. [Performance Issues](#performance-issues)
6. [Error Messages](#error-messages)

---

## 🛠️ Installation Issues

### Problem: `pip install` Fails

**Symptoms**:
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solutions**:

1. **Update pip**:
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Check Python version**:
   ```bash
   python --version  # Should be 3.8+
   ```

3. **Install individually**:
   ```bash
   pip install PyQt5
   pip install SpeechRecognition
   pip install pyaudio
   # ... etc
   ```

4. **Platform-specific fix**:
   
   **macOS**:
   ```bash
   brew install portaudio
   pip install pyaudio
   ```
   
   **Ubuntu/Linux**:
   ```bash
   sudo apt-get install python3-pyaudio
   sudo apt-get install portaudio19-dev
   pip install pyaudio
   ```
   
   **Windows**:
   - Download PyAudio wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
   - Install: `pip install PyAudio-0.2.11-cp38-cp38-win_amd64.whl`

---

### Problem: Module Not Found Errors

**Symptoms**:
```
ModuleNotFoundError: No module named 'dotenv'
```

**Solution**:
```bash
# Install missing module
pip install python-dotenv

# Or reinstall all requirements
pip install -r requirements.txt
```

---

### Problem: Permission Denied

**Symptoms**:
```
PermissionError: [Errno 13] Permission denied
```

**Solutions**:

1. **Run with user install**:
   ```bash
   pip install --user -r requirements.txt
   ```

2. **Use virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

3. **Check file permissions**:
   ```bash
   chmod +x main.py
   ```

---

## 🎤 Voice Recognition Problems

### Problem: Microphone Not Detected

**Symptoms**:
- "Cannot access microphone" error
- No audio input detected
- App crashes on start

**Solutions**:

1. **Check microphone connection**:
   - Verify mic is plugged in
   - Test in other apps (Zoom, Discord, etc.)
   - Try different USB port (if USB mic)

2. **Grant permissions**:
   
   **Windows**:
   - Settings → Privacy → Microphone
   - Enable for desktop apps
   
   **macOS**:
   - System Preferences → Security & Privacy → Microphone
   - Add Python to allowed apps
   
   **Linux**:
   ```bash
   # Check if user is in audio group
   groups
   # Add if missing
   sudo usermod -a -G audio $USER
   ```

3. **List available microphones**:
   ```bash
   python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
   ```

4. **Set default microphone**:
   - Windows: Sound Settings → Input
   - macOS: System Preferences → Sound → Input
   - Linux: `alsamixer` or PulseAudio control

---

### Problem: Voice Not Recognized

**Symptoms**:
- Microphone lights up but no transcription
- "Could not understand audio" errors
- Commands not detected

**Solutions**:

1. **Check internet connection**:
   ```bash
   ping google.com
   ```
   Voice recognition requires internet!

2. **Improve audio quality**:
   - Reduce background noise
   - Speak directly into microphone
   - Adjust microphone distance (6-12 inches ideal)
   - Increase microphone volume in system settings

3. **Test microphone**:
   ```bash
   # Open Python
   python
   ```
   ```python
   import speech_recognition as sr
   r = sr.Recognizer()
   with sr.Microphone() as source:
       print("Say something!")
       audio = r.listen(source)
       try:
           print(r.recognize_google(audio))
       except Exception as e:
           print(f"Error: {e}")
   ```

4. **Adjust recognition settings**:
   Edit `main.py`:
   ```python
   self.recognizer.energy_threshold = 1200  # Lower for quiet, higher for noisy
   self.recognizer.pause_threshold = 0.8    # Time to wait before processing
   ```

---

### Problem: Wrong Language Detected

**Symptoms**:
- Commands in English recognized as gibberish
- Wrong language transcription

**Solution**:
1. Right-click microphone → Select Language
2. Choose correct language
3. Test with simple command

---

### Problem: Auto-Stop Too Fast/Slow

**Symptoms**:
- Mic stops listening mid-sentence
- Takes too long to process command

**Solution**:
Edit `main.py`:
```python
# Line ~119
self.silence_timeout = 4.0  # Increase for slower, decrease for faster
```

---

## 🤖 API & AI Issues

### Problem: "All API Providers Failed"

**Symptoms**:
```
[ERROR] All API providers failed. Please check your API keys
```

**Solutions**:

1. **Verify .env file exists**:
   ```bash
   ls -la .env  # Should exist in project root
   ```

2. **Check API keys format**:
   ```env
   # .env file should look like:
   GROQ_API_KEY=gsk_xxxxxxxxxxxxx
   GEMINI_API_KEY=AIzaxxxxxxxxxxxxx
   ```
   - No quotes around keys
   - No spaces
   - Correct variable names

3. **Test API keys manually**:
   ```bash
   python
   ```
   ```python
   import os
   from dotenv import load_dotenv
   load_dotenv()
   print(os.getenv('GROQ_API_KEY'))  # Should print your key
   ```

4. **Check API key validity**:
   - Go to provider's website
   - Verify key hasn't expired
   - Check usage limits
   - Regenerate if necessary

5. **Test with single provider**:
   Edit `config.json`:
   ```json
   {
     "api_priority": ["groq"]  # Test one at a time
   }
   ```

---

### Problem: API Rate Limit Exceeded

**Symptoms**:
```
[RATE_LIMIT] GROQ: Rate limit exceeded
```

**Solutions**:

1. **Wait for rate limit reset** (usually 1 minute to 1 hour)

2. **Use different provider**:
   The system automatically fails over, but you can change priority:
   ```json
   "api_priority": ["gemini", "groq", "deepseek"]
   ```

3. **Reduce usage**:
   - Wait between commands
   - Use manual command entry for complex queries

4. **Upgrade API plan** (if using free tier)

---

### Problem: Slow API Responses

**Symptoms**:
- Long wait times after speaking
- Timeout errors

**Solutions**:

1. **Check internet speed**:
   ```bash
   speedtest-cli
   ```

2. **Reduce timeout**:
   Edit `config.json`:
   ```json
   {
     "timeout_seconds": 15  # Reduce from 30
   }
   ```

3. **Switch to faster provider**:
   - Groq is usually fastest
   - DeepSeek is good alternative

---

## 🎯 Feature-Specific Issues

### Observer Not Working

**Problem**: Tracker won't start

**Solutions**:

1. **Check PID file**:
   ```bash
   rm Observer/tracker.pid  # Delete stale PID file
   ```

2. **Install platform dependencies**:
   
   **Windows**:
   ```bash
   pip install pywin32
   ```
   
   **Linux**:
   ```bash
   sudo apt-get install gir1.2-wnck-3.0
   pip install pygobject
   ```
   
   **macOS**:
   ```bash
   pip install pyobjc-framework-Cocoa
   ```

3. **Check permissions**:
   - Windows: Run as Administrator (if needed)
   - macOS: Grant accessibility permissions
   - Linux: Check X11/Wayland compatibility

4. **Check logs**:
   ```bash
   cat logs/observer.log
   tail -f logs/observer.log  # Real-time monitoring
   ```

5. **Manual test**:
   ```bash
   cd Observer
   python tracker.py
   ```

---

**Problem**: Dashboard not opening

**Solutions**:

1. **Check if server is running**:
   ```bash
   lsof -i :8000  # Check if port 8000 is in use
   ```

2. **Start server manually**:
   ```bash
   cd Observer
   python server.py
   ```

3. **Try different browser**:
   - Open manually: `http://localhost:8000/dashboard.html`

4. **Check firewall**:
   - Allow port 8000
   - Disable temporarily to test

---

### WhatsApp Automation Issues

**Problem**: Chrome debugging port error

**Solutions**:

1. **Close all Chrome instances**:
   ```bash
   # Windows
   taskkill /F /IM chrome.exe
   
   # macOS/Linux
   killall "Google Chrome"
   ```

2. **Start Chrome with debugging**:
   ```bash
   # Windows
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
   
   # macOS
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
   
   # Linux
   google-chrome --remote-debugging-port=9222
   ```

3. **Check port availability**:
   ```bash
   netstat -an | grep 9222
   ```

4. **Use different port**:
   Edit code to use 9223 or 9224

---

**Problem**: Message not sending

**Solutions**:

1. **Verify WhatsApp Web login**:
   - Go to web.whatsapp.com
   - Make sure QR is scanned
   - Check "Keep me signed in"

2. **Check contact name**:
   - Use exact name from WhatsApp
   - Try first name only
   - Case doesn't matter

3. **Wait for page load**:
   - WhatsApp Web needs time to load
   - Try again after 5-10 seconds

4. **Check logs**:
   ```bash
   cat logs/whatsapp_bridge.log
   ```

---

### Form Filler Issues

**Problem**: Fields not getting filled

**Solutions**:

1. **Verify Chrome debugging**:
   - Chrome must be running with port 9222
   - Only one instance can use debugging port

2. **Check user data**:
   ```bash
   cat Auto_Form_Filler/user_data.json
   # Verify JSON is valid
   ```

3. **Ensure all fields visible**:
   - Scroll to make fields visible
   - Form filler can't fill hidden fields

4. **Check field detection**:
   - Look at console output
   - Should show detected fields

5. **Manual test**:
   ```bash
   cd Auto_Form_Filler
   python form_filler_launcher.py
   ```

---

### File Operations Issues

**Problem**: "Permission denied" errors

**Solutions**:

1. **Check file/folder permissions**:
   ```bash
   ls -la /path/to/file
   ```

2. **Verify file isn't in use**:
   - Close programs using the file
   - Windows: Use Resource Monitor
   - macOS/Linux: `lsof /path/to/file`

3. **Run with appropriate permissions**:
   - Avoid running as admin unless necessary
   - Check folder ownership

---

**Problem**: Files not organizing correctly

**Solutions**:

1. **Test in dry-run mode first**:
   ```python
   from file_operations_bridge import organize_folder
   organize_folder("downloads", dry_run=True)
   ```

2. **Check folder path**:
   - Use full path if relative doesn't work
   - Check spelling

3. **Verify folder exists**:
   ```bash
   ls -la ~/Downloads
   ```

---

## ⚡ Performance Issues

### Problem: High CPU Usage

**Symptoms**:
- Fan running loud
- System lag
- 100% CPU

**Solutions**:

1. **Check which component**:
   ```bash
   top  # Linux/macOS
   # Task Manager → Details (Windows)
   ```

2. **If Observer is culprit**:
   - Increase check interval in `Observer/config.json`:
   ```json
   {
     "check_interval_seconds": 5  # Increase from 2
   }
   ```

3. **If voice recognition is culprit**:
   - Close other audio apps
   - Reduce energy threshold sensitivity

4. **General optimization**:
   - Close unused features
   - Disable audio feedback if not needed
   - Reduce logging level

---

### Problem: High RAM Usage

**Symptoms**:
- Memory warnings
- System slowdown
- Swap usage high

**Solutions**:

1. **Check memory usage**:
   ```bash
   ps aux | grep python
   ```

2. **Restart application**:
   - Long-running instances may leak memory
   - Restart every few hours if needed

3. **Disable features**:
   - Settings → Features
   - Disable unused modules

---

### Problem: Slow Response Time

**Symptoms**:
- Delay after speaking
- Lag in UI
- Commands timeout

**Solutions**:

1. **Check internet speed** (for AI/voice recognition)

2. **Reduce logging**:
   Edit `logger_config.py`:
   ```python
   level=logging.WARNING  # Instead of INFO
   ```

3. **Clear old logs**:
   ```bash
   rm -rf logs/*
   python main.py
   ```

4. **Optimize database** (Observer):
   ```bash
   sqlite3 Observer/productivity_data.db "VACUUM;"
   ```

---

## 🚨 Error Messages

### Error: "WNDPROC Error"

**Full error**:
```
win32gui.error: (0, 'RegisterClass', 'No error message is available')
```

**Solution**:
This is a Windows notification issue. Fixed by using `plyer` instead of `win10toast`:
```bash
pip uninstall win10toast
pip install plyer
```

---

### Error: "ModuleNotFoundError: win32gui"

**Solution**:
```bash
pip install pywin32
```

---

### Error: "PortAudio library not found"

**Solution**:

**macOS**:
```bash
brew install portaudio
pip install --upgrade pyaudio
```

**Ubuntu/Linux**:
```bash
sudo apt-get install portaudio19-dev
pip install --upgrade pyaudio
```

**Windows**:
Download PyAudio wheel and install manually

---

### Error: "Could not import gobject"

**Solution** (Linux):
```bash
sudo apt-get install python3-gi python3-gi-cairo gir1.2-wnck-3.0
```

---

### Error: "SQLite operational error"

**Solution**:
```bash
# Delete and recreate database
rm Observer/productivity_data.db
cd Observer
python setup_database.py
```

---

## 📊 Diagnostic Tools

### Check All Dependencies

```bash
python -c "
import sys
modules = ['PyQt5', 'speech_recognition', 'dotenv', 'requests', 'psutil']
for m in modules:
    try:
        __import__(m)
        print(f'✓ {m}')
    except:
        print(f'✗ {m} - MISSING')
"
```

### View Logs

```bash
# All logs
ls -lh logs/

# Latest errors
tail -n 50 logs/error.log

# Real-time monitoring
tail -f logs/main.log
```

### Test Components Individually

```bash
# Test API handler
python api_handler.py

# Test intent classifier
python Intent_classifier.py

# Test file operations
python file_operations_bridge.py

# Test Observer
cd Observer && python tracker.py
```

---

## 🆘 Still Having Issues?

### Gather Diagnostic Info

```bash
# System info
python --version
pip list
uname -a  # Linux/macOS
systeminfo  # Windows

# Check logs
cat logs/error.log
```

### Get Help

1. **Check documentation**:
   - README.md
   - USER_GUIDE.md
   - This file

2. **Search existing issues**:
   - GitHub Issues
   - Closed issues might have solution

3. **Create new issue**:
   - Include: OS, Python version, error message, logs
   - Use bug report template
   - Be specific about steps to reproduce

4. **Community help**:
   - GitHub Discussions
   - Stack Overflow (tag: voice-command-ai)

---

## 📞 Contact

- **GitHub Issues**: [Report Bug](https://github.com/yourusername/voice-command-ai/issues)
- **Discussions**: [Ask Question](https://github.com/yourusername/voice-command-ai/discussions)
- **Email**: support@example.com

---

<div align="center">

**Tip**: When reporting bugs, always include the contents of `logs/error.log`!

<sub>Last updated: February 2026</sub>

</div>

# 📚 USER GUIDE
## Voice Command AI Desktop Automation System

Welcome to the complete user guide! This document will teach you everything you need to know to become a power user.

---

## 📖 Table of Contents

1. [Getting Started](#getting-started)
2. [Voice Commands](#voice-commands)
3. [Feature Guides](#feature-guides)
4. [Tips & Tricks](#tips--tricks)
5. [FAQ](#faq)

---

## 🚀 Getting Started

### First Launch

When you first run the application:

1. **Microphone Button Appears** - A floating button in the top-right corner
2. **Check Internet** - Voice recognition requires internet
3. **Test Your Microphone** - Click the button and say "hello"
4. **Grant Permissions** - Allow microphone access if prompted

### The Interface

#### Microphone Button States

| State | Appearance | Meaning |
|-------|-----------|---------|
| 🔵 Blue | Idle | Ready to listen |
| 🔴 Red | Pulsing | Currently listening |
| ⚫ Gray | Disabled | Error or offline |

#### Button Actions

- **Left Click**: Toggle listening on/off
- **Right Click**: Open menu
- **Drag**: Move button to new position

### Your First Commands

Try these simple commands to get started:

1. Click the mic button (it turns red)
2. Say: **"search for cute cats"**
3. Watch as Google search opens!

More beginner commands:
- "open chrome"
- "take screenshot"
- "play music on youtube"

---

## 🎤 Voice Commands

### 🔍 Web & Search Commands

#### Google Search
```
"search for [query]"
"google [query]"
"find information about [topic]"
"look up [query]"
```

**Examples**:
- "search for python tutorials"
- "google weather in New York"
- "find information about quantum physics"

#### YouTube
```
"play [song/video] on youtube"
"youtube [query]"
```

**Examples**:
- "play despacito on youtube"
- "play cat videos on youtube"
- "youtube how to cook pasta"

#### Spotify
```
"play [song/playlist] on spotify"
"spotify [query]"
```

**Examples**:
- "play jazz on spotify"
- "spotify workout playlist"

#### Open Websites
```
"open website [url]"
"go to [url]"
```

**Examples**:
- "open website github.com"
- "go to reddit.com"

---

### 💬 Messaging Commands

#### Send WhatsApp Messages
```
"send [contact] as [message]"
"send message to [contact] as [message]"
"whatsapp [contact] as [message]"
```

**Examples**:
- "send John as hello how are you"
- "send message to Sarah as meeting at 3pm"
- "whatsapp Mom as I'll be home late"

**Tips**:
- Use contact's first name
- Speak clearly for the message
- Long messages work too!

---

### 📁 File Operations

#### Organize Files
```
"organize my [folder]"
"organize [folder name]"
"sort my [folder]"
```

**Examples**:
- "organize my downloads"
- "organize documents"
- "sort my desktop"

**What it does**:
- Creates folders: Images, Documents, Videos, Audio, Code, Archives, Others
- Moves files to appropriate folders
- Handles name conflicts automatically

#### Compress Files/Folders
```
"compress [folder/file]"
"zip [folder/file]"
"compress my [folder]"
```

**Examples**:
- "compress my project folder"
- "zip documents"
- "compress vacation photos"

**Result**:
- Creates .zip file with timestamp
- Saves in same location as original

#### Extract Archives
```
"extract [archive name]"
"unzip [archive name]"
```

**Examples**:
- "extract data.zip"
- "unzip project_backup.zip"

**Result**:
- Creates folder with archive name
- Extracts all files inside

#### Delete Files
```
"delete [file/folder]"
"remove [file/folder]"
```

**Examples**:
- "delete old files"
- "remove temp folder"

**Safety**:
- Always asks for confirmation
- Shows file size before deleting
- Can be cancelled

---

### 🖥️ System Control

#### Screenshots
```
"take screenshot"
"screenshot"
"capture screen"
```

**Result**:
- Saves to Pictures/Screenshots/
- Filename: screenshot_YYYYMMDD_HHMMSS.png

#### Volume Control
```
"set volume to [number]"
"volume [number]"
"mute"
"unmute"
```

**Examples**:
- "set volume to 50"
- "volume 100"
- "mute"

**Range**: 0-100

#### Lock Screen
```
"lock screen"
"lock computer"
"lock my computer"
```

**Platforms**:
- ✅ Windows
- ✅ macOS
- ✅ Linux (multiple DEs)

#### Shutdown (with confirmation)
```
"shutdown"
"shutdown computer"
"restart"
"restart computer"
```

**Safety**:
- Requires typing "yes" to confirm
- 10-second countdown
- Can be cancelled

---

### 🖱️ Application Control

#### Open Applications
```
"open [app name]"
"launch [app name]"
"start [app name]"
"run [app name]"
```

**Examples**:
- "open chrome"
- "launch notepad"
- "start calculator"
- "run firefox"

**Supported Apps**:
- Browsers: Chrome, Firefox, Edge, Safari
- Office: Word, Excel, PowerPoint
- Tools: Notepad, Calculator, Terminal
- Any installed application (use exact name)

#### Close Applications
```
"close [app name]"
"quit [app name]"
"exit [app name]"
"kill [app name]"
```

**Examples**:
- "close chrome"
- "quit spotify"
- "exit notepad"

---

### 📊 Productivity (Observer)

#### View Productivity
```
"show my productivity"
"show productivity stats"
"check my productivity"
```

**Result**:
- Opens web dashboard
- Shows app usage breakdown
- Displays productivity score
- Charts and graphs

#### Check Status
```
"check observer status"
"observer status"
"show tracking status"
```

**Shows**:
- Whether tracking is active
- Database status
- Session information

#### Toggle Tracking

**Enable/Disable via**:
- Right-click menu → Observer ON/OFF
- Cannot be voice controlled (security)

---

### 📝 Form Filling

#### Start Form Filling
```
"start form filling"
"enable form filler"
"activate form filler"
```

**Requirements**:
- Chrome running with debugging port 9222
- Form data configured

#### Update Personal Info
```
"update my personal info"
"edit my information"
```

**Opens**:
- Settings dialog
- Form data editor

---

## 🎯 Feature Guides

### Observer - Detailed Guide

#### What is Observer?

Observer is your personal productivity tracker that:
- Records which apps you use
- Tracks how long you use them
- Categorizes them as productive/unproductive
- Generates daily reports

#### How to Use

1. **Enable Tracking**:
   - Right-click mic button
   - Select "Start Observer Tracking"

2. **Work Normally**:
   - Observer runs in background
   - Minimal resource usage
   - Privacy-focused (sanitizes passwords, etc.)

3. **View Reports**:
   - Say "show my productivity"
   - Browse dashboard at localhost:8000
   - See charts, stats, top apps

4. **Stop Tracking**:
   - Right-click → "Stop Observer Tracking"

#### Dashboard Features

- **Today's Summary**: Time spent, productivity score
- **App Breakdown**: Pie chart of app usage
- **Timeline**: Hourly activity graph
- **Top Apps**: Most used applications
- **Weekly Trends**: 7-day productivity trends

#### Categories

**Productive**:
- Code editors (VS Code, PyCharm)
- Office apps (Word, Excel)
- Professional tools

**Communication**:
- Slack, Teams, Email
- WhatsApp, Discord

**Browsing**:
- Chrome, Firefox
- General web browsing

**Entertainment**:
- YouTube, Netflix
- Games, Social Media

#### Privacy

Observer protects your privacy:
- ✅ Sanitizes passwords in window titles
- ✅ Redacts banking/payment info
- ✅ Hides email content
- ✅ All data stored locally
- ✅ No cloud upload

---

### WhatsApp Automation - Detailed Guide

#### Setup

1. **Install Chrome** (if not installed)

2. **Open Chrome with Debugging**:
   ```bash
   # Windows
   chrome.exe --remote-debugging-port=9222
   
   # macOS
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
   
   # Linux
   google-chrome --remote-debugging-port=9222
   ```

3. **Login to WhatsApp Web**:
   - Go to web.whatsapp.com
   - Scan QR code with phone
   - Keep logged in

4. **Use Voice Commands**:
   - "send John as hello"
   - Message gets sent automatically!

#### Two Modes

**1. Manual Send (Quick)**:
- One-time message
- Immediate send
- Chrome closes after

**2. Automated Chatbot**:
- Continuous operation
- AI-powered responses
- Uses ChatGPT integration

To use Chatbot mode:
```bash
cd Chat_Automation
python main.py
# Select option 1
```

#### Tips

- Use first names for contacts
- Clear pronunciation helps
- Longer messages work fine
- Can send emojis (speak them: "send John as hello smiley face")

---

### Auto Form Filler - Detailed Guide

#### What Forms are Supported?

- ✅ Contact forms
- ✅ Registration forms
- ✅ Job applications
- ✅ Survey forms
- ✅ Multi-page forms

#### Setup Your Data

Edit `Auto_Form_Filler/user_data.json`:

```json
{
  "personal_info": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@email.com",
    "phone": "+1234567890",
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip": "10001"
  },
  "education": {
    "university": "University Name",
    "degree": "Bachelor's",
    "major": "Computer Science",
    "graduation_year": "2020"
  },
  "professional": {
    "company": "Company Name",
    "position": "Software Engineer",
    "experience_years": "5",
    "skills": "Python, JavaScript, AI"
  }
}
```

#### How to Use

1. **Open Chrome with Debugging**:
   ```bash
   chrome --remote-debugging-port=9222
   ```

2. **Navigate to Form**:
   - Go to any website with a form
   - Make sure all fields are visible

3. **Activate Form Filler**:
   - Say "start form filling"
   - Or run manually: `python Auto_Form_Filler/form_filler_launcher.py`

4. **Watch Magic Happen**:
   - Fields get detected
   - AI matches fields to your data
   - Form fills automatically
   - Multi-page forms handled

#### The 8 Gates System

1. **Gate 1**: Detect all form fields
2. **Gate 2**: Match fields to user data
3. **Gate 3**: Validate AI suggestions
4. **Gate 4**: Fill basic fields
5. **Gate 5**: Handle complex fields (dropdowns, radio)
6. **Gate 6**: Verify filled data
7. **Gate 7**: Track multi-page forms
8. **Gate 8**: Learn new question patterns

#### Learning System

Form filler gets smarter:
- Learns new field types
- Remembers custom questions
- Improves matching over time
- Stores learned patterns

---

## 💡 Tips & Tricks

### Voice Recognition Tips

1. **Speak Clearly**: Enunciate words
2. **Normal Pace**: Not too fast, not too slow
3. **Quiet Environment**: Reduces background noise
4. **Good Microphone**: Better hardware = better recognition
5. **Consistent Distance**: Stay same distance from mic

### Improving Accuracy

1. **Use Full Sentences**: "organize my downloads" vs "organize downloads"
2. **Be Specific**: "play despacito on youtube" vs "play song"
3. **Pause Between Commands**: Wait for one to finish
4. **Check Logs**: Review `logs/classifier.log` for mis-classifications

### Speed Tips

1. **Quick Commands**: Use shortest form
   - "search cats" instead of "search for cute cats"
   - "play music" instead of "play some music on youtube"

2. **Keyboard Shortcuts**: Right-click menu has hotkeys

3. **Manual Mode**: Right-click → Manual Command for typing

### Customization

1. **Change Language**:
   - Right-click → Select Language
   - 13 languages supported

2. **Move Button**:
   - Drag it anywhere on screen
   - Position persists across sessions

3. **Disable Features**:
   - Right-click → Settings → Features
   - Toggle what you don't use

---

## ❓ FAQ

### General

**Q: Does this work offline?**
A: Voice recognition requires internet, but some features work offline.

**Q: Which operating systems are supported?**
A: Windows 10/11, macOS 10.14+, Ubuntu 20.04+ (most Linux distros).

**Q: Is my data private?**
A: Yes! All data stays on your computer. API calls only send commands, not personal data.

**Q: Can I use it in other languages?**
A: Yes! Supports 13 languages including English, Spanish, French, Hindi, Chinese, Japanese, and more.

### Voice Recognition

**Q: Why isn't it understanding me?**
A: Check:
- Microphone permissions granted
- Internet connection active
- Background noise minimal
- Speaking clearly and at normal pace

**Q: Can I use a wake word like "Hey Siri"?**
A: Not yet. Currently requires clicking the button. Wake word planned for v2.0.

**Q: What if I have an accent?**
A: Google Speech Recognition handles most accents well. Try speaking slightly slower.

### Features

**Q: Can Observer track time in specific documents?**
A: It tracks applications, not individual documents (for privacy).

**Q: Does WhatsApp automation violate ToS?**
A: Use at your own risk. We recommend manual mode for important conversations.

**Q: How accurate is form filling?**
A: 90%+ accuracy for standard forms. Always review before submitting!

**Q: Can it fill CAPTCHA?**
A: No, CAPTCHAs must be solved manually.

### Technical

**Q: How much RAM does it use?**
A: Typically 100-200 MB. Observer adds ~50 MB when active.

**Q: Can I run multiple instances?**
A: No, only one instance per system (prevents conflicts).

**Q: Where are logs stored?**
A: In the `logs/` directory. Helpful for troubleshooting.

**Q: Can I contribute?**
A: Yes! Check CONTRIBUTING.md for guidelines.

---

## 🆘 Need More Help?

- 📖 **Full Documentation**: See README.md
- 🔧 **Troubleshooting**: See TROUBLESHOOTING.md
- 📝 **Command Reference**: See COMMANDS_CHEATSHEET.md
- 🐛 **Report Bug**: Open GitHub issue
- 💬 **Ask Question**: GitHub Discussions

---

## 🎓 Advanced Usage

Coming soon:
- Creating custom commands
- Extending with plugins
- API integration guide
- Automation workflows

---

**Happy Voice Commanding! 🎤**

<div align="center">
<sub>Last updated: February 2026</sub>
</div>

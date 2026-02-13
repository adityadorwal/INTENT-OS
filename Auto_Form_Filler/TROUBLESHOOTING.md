# Auto Form Filler - Troubleshooting Guide

## Problem: CMD closes immediately after entering the form link

### Root Causes:
1. Chrome is not running with debugging enabled
2. The core script can't connect to Chrome
3. Python/Selenium errors that close the console too quickly

### Solutions:

## Step 1: Test Chrome Connection

Run the test script first:
```bash
cd Auto_Form_Filler
python test_connection.py
```

This will tell you if Chrome debugging is working.

## Step 2: Make Sure Chrome is Running with Debugging

### Option A: Let the launcher start Chrome (Recommended)
- Close ALL Chrome windows
- Run the form filler launcher
- It will automatically start Chrome with debugging enabled

### Option B: Start Chrome manually
```bash
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Users\aakri\AppData\Local\Google\Chrome\User Data\Default"
```

## Step 3: Check for Common Issues

### Issue 1: Port Already in Use
- Close all Chrome instances
- Check Task Manager for any lingering chrome.exe processes
- Kill them and try again

### Issue 2: Profile Path is Wrong
- Check `chrome_profile.json` in the parent directory
- Make sure `profile_path` points to a valid Chrome profile
- Current path: `C:\Users\aakri\AppData\Local\Google\Chrome\User Data\Default`

### Issue 3: Selenium/ChromeDriver Issues
- Make sure ChromeDriver is installed and in PATH
- Update ChromeDriver to match your Chrome version
- Install: `pip install selenium --upgrade`

### Issue 4: Missing Dependencies
```bash
pip install selenium
pip install psutil
```

## Step 4: Run Core Script Manually (For Debugging)

1. Start Chrome with debugging (see Step 2)
2. Open the form in Chrome
3. Run the core script manually:
```bash
cd Auto_Form_Filler
python auto_form_filler_core.py
```

This will show you the exact error message.

## Step 5: Check Logs

The core script now keeps the console open on errors. Look for:
- "Chrome connection failed" - Chrome not running with debugging
- "Chrome config not found" - Missing chrome_profile.json
- "Form not detected" - Not on a Google Form page

## Quick Fix Checklist

- [ ] Chrome is closed completely
- [ ] Run `python test_connection.py` - does it work?
- [ ] `chrome_profile.json` exists in parent directory
- [ ] Selenium is installed: `pip install selenium`
- [ ] ChromeDriver is installed and matches Chrome version
- [ ] Port 9222 is not blocked by firewall
- [ ] You're on a Google Form page (docs.google.com/forms)

## Still Not Working?

Run this diagnostic:
```bash
# Check Python
python --version

# Check Selenium
pip show selenium

# Check ChromeDriver
chromedriver --version

# Test Chrome connection
cd Auto_Form_Filler
python test_connection.py
```

## Contact Support

If none of these work, provide:
1. Output from `test_connection.py`
2. Error message from the core script console
3. Chrome version: chrome://version
4. Python version: `python --version`

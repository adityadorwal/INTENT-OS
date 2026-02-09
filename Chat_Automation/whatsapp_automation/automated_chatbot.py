"""
WhatsApp Automated Chatbot - COMPLETE VERSION
✅ Uses working send_message approach
✅ Smart detection system
✅ Desktop alerts
✅ API handler
✅ Conversation summary on stop
✅ All features integrated WITHOUT breaking message loop
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time
import threading
import random
from datetime import datetime
import json
import os
import requests

# Import the WORKING code
from chrome_manager import ChromeManager
from whatsapp_helper import WhatsAppHelper


class SmartDetection:
    """Detection system - doesn't interrupt loop"""
    
    DETECTION_KEYWORD = "DETECTION_ALERT_CODE_RED_9999"
    
    def __init__(self):
        self.detection_log = []
    
    def create_detection_prompt(self, user_message, contact_name, relation):
        """Add detection check to prompt"""
        prompt = f"""You're chatting with {contact_name}, your {relation}.

New message from {contact_name}:
{user_message}

🚨 CRITICAL - CHECK FIRST:
If this message suggests they suspect you're AI/bot/automated, reply EXACTLY:
{self.DETECTION_KEYWORD}

Suspicious examples:
- "are you a bot?"
- "you reply too fast"
- "is this automated?"
- "you sound like AI"
- "prove you're human"

IF SUSPICIOUS → Reply only: {self.DETECTION_KEYWORD}

IF NORMAL → Reply naturally:
- 1-2 sentences max
- Casual, friendly
- Match their energy
- Sound human

Your reply:"""
        
        return prompt
    
    def check_response(self, ai_response, user_message):
        """Check if AI detected suspicion"""
        if self.DETECTION_KEYWORD in ai_response:
            self.log_detection(user_message)
            return {'detected': True, 'message': user_message}
        
        return {'detected': False, 'response': self.clean_response(ai_response)}
    
    def clean_response(self, response):
        """Clean AI response"""
        import re
        ai_phrases = ["As an AI", "I'm an AI", "I'm ChatGPT", "I'm an artificial intelligence"]
        for phrase in ai_phrases:
            response = re.sub(phrase, "", response, flags=re.IGNORECASE)
        response = re.sub(r'\*\*(.*?)\*\*', r'\1', response)
        response = re.sub(r'\s+', ' ', response).strip()
        return response
    
    def log_detection(self, message):
        """Log detection"""
        self.detection_log.append({
            'timestamp': datetime.now().isoformat(),
            'message': message
        })


class DesktopAlerts:
    """Non-blocking alert system"""
    
    def __init__(self):
        self.setup_notifications()
    
    def setup_notifications(self):
        """Setup plyer if available"""
        try:
            from plyer import notification
            self.has_plyer = True
            self.notification = notification
        except ImportError:
            self.has_plyer = False
    
    def send_detection_alert(self, contact, message):
        """Alert for detection"""
        print(f"\n🚨 DETECTION ALERT from {contact}: {message}\n")
        
        if self.has_plyer:
            try:
                self.notification.notify(
                    title='🚨 BOT DETECTION!',
                    message=f'{contact}: {message[:100]}',
                    app_name='WhatsApp Bot',
                    timeout=10
                )
            except:
                pass
        
        # Sound
        try:
            import winsound
            for _ in range(3):
                winsound.MessageBeep(winsound.MB_ICONHAND)
                time.sleep(0.3)
        except:
            print('\a')
    
    def show_summary(self, contact, summary):
        """Show conversation summary"""
        print(f"\n📊 CONVERSATION SUMMARY - {contact}")
        print("="*60)
        print(summary)
        print("="*60 + "\n")
        
        if self.has_plyer:
            try:
                self.notification.notify(
                    title=f'📊 Summary - {contact}',
                    message='Conversation summary ready!',
                    app_name='WhatsApp Bot',
                    timeout=10
                )
            except:
                pass


class WhatsAppAPIHandler:
    """API handler with Groq"""
    
    def __init__(self):
        self.config_file = "whatsapp_api_config.json"
        self.api_key = self.load_api_key()
    
    def load_api_key(self):
        """Load API key"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('api_keys', {}).get('groq', '')
            except:
                return ''
        return ''
    
    def save_api_key(self, api_key):
        """Save API key"""
        config = {
            "api_keys": {"groq": api_key},
            "api_priority": ["groq"],
            "timeout_seconds": 30
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        self.api_key = api_key
    
    def generate_response(self, prompt):
        """Generate response"""
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200,
                "temperature": 0.9
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"❌ API error: {e}")
            return None
    
    def generate_summary(self, contact, relation, conversation_history):
        """Generate conversation summary"""
        # Format last 20 messages
        conv_text = "\n".join([
            f"{msg.get('sender', 'Unknown')}: {msg.get('message', '')}"
            for msg in conversation_history[-20:]
        ])
        
        prompt = f"""Summarize this WhatsApp conversation with {contact} (my {relation}).

Conversation:
{conv_text}

Provide brief summary:
- Main topics discussed
- Key points or decisions
- Overall tone/mood
- Important information

Keep it concise (3-5 sentences):"""
        
        return self.generate_response(prompt)


class CompleteWhatsAppBot:
    """Complete bot with all features"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Chatbot - Complete")
        self.root.geometry("850x750")
        self.root.configure(bg='#075E54')
        
        # Systems
        self.api_handler = WhatsAppAPIHandler()
        self.detection = SmartDetection()
        self.alerts = DesktopAlerts()
        
        # Bot state
        self.is_running = False
        self.bot_thread = None
        self.driver = None
        self.chrome_manager = None
        self.wa_helper = None
        
        # Stats
        self.message_count = 0
        self.last_replied = ""
        self.conversation_history = []
        
        # Create GUI
        self.create_gui()
    
    def create_gui(self):
        """Create GUI"""
        # Title
        title_frame = tk.Frame(self.root, bg='#128C7E', pady=15)
        title_frame.pack(fill='x')
        
        tk.Label(
            title_frame,
            text="🤖 WhatsApp Chatbot - Complete",
            font=('Arial', 18, 'bold'),
            bg='#128C7E',
            fg='white'
        ).pack()
        
        # Main
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # API Key
        api_frame = tk.LabelFrame(main_frame, text="🔑 API Key (Groq)", font=('Arial', 12, 'bold'), bg='#f0f0f0', padx=15, pady=10)
        api_frame.pack(fill='x', pady=(0, 10))
        
        key_row = tk.Frame(api_frame, bg='#f0f0f0')
        key_row.pack(fill='x')
        
        tk.Label(key_row, text="API Key:", font=('Arial', 10), bg='#f0f0f0', width=12, anchor='w').pack(side='left')
        self.api_key_entry = tk.Entry(key_row, font=('Arial', 10), width=50, show='*')
        self.api_key_entry.pack(side='left', padx=5, fill='x', expand=True)
        if self.api_handler.api_key:
            self.api_key_entry.insert(0, self.api_handler.api_key)
        
        tk.Button(key_row, text="💾 Save", command=self.save_api_key, bg='#4CAF50', fg='white', padx=10).pack(side='left', padx=5)
        
        # Config
        config_frame = tk.LabelFrame(main_frame, text="⚙️ Configuration", font=('Arial', 12, 'bold'), bg='#f0f0f0', padx=15, pady=10)
        config_frame.pack(fill='x', pady=(0, 10))
        
        row1 = tk.Frame(config_frame, bg='#f0f0f0')
        row1.pack(fill='x', pady=5)
        tk.Label(row1, text="Contact Name:", font=('Arial', 10), bg='#f0f0f0', width=15, anchor='w').pack(side='left')
        self.contact_entry = tk.Entry(row1, font=('Arial', 10), width=40)
        self.contact_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        row2 = tk.Frame(config_frame, bg='#f0f0f0')
        row2.pack(fill='x', pady=5)
        tk.Label(row2, text="Relationship:", font=('Arial', 10), bg='#f0f0f0', width=15, anchor='w').pack(side='left')
        self.relation_entry = tk.Entry(row2, font=('Arial', 10), width=40)
        self.relation_entry.pack(side='left', padx=5, fill='x', expand=True)
        self.relation_entry.insert(0, "friend")
        
        # Controls
        control_frame = tk.Frame(main_frame, bg='#f0f0f0')
        control_frame.pack(fill='x', pady=15)
        
        self.start_btn = tk.Button(control_frame, text="▶️ START", command=self.start_bot, bg='#25D366', fg='white', font=('Arial', 14, 'bold'), padx=30, pady=10)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ STOP & SUMMARY", command=self.stop_bot, bg='#dc3545', fg='white', font=('Arial', 14, 'bold'), padx=20, pady=10, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        # Status
        status_frame = tk.LabelFrame(main_frame, text="📊 Status", font=('Arial', 12, 'bold'), bg='#f0f0f0', padx=15, pady=10)
        status_frame.pack(fill='x', pady=(0, 10))
        
        self.status_label = tk.Label(status_frame, text="⚫ Status: Idle", font=('Arial', 11), bg='#f0f0f0', anchor='w')
        self.status_label.pack(fill='x', pady=2)
        
        self.messages_label = tk.Label(status_frame, text="💬 Messages: 0", font=('Arial', 10), bg='#f0f0f0', anchor='w')
        self.messages_label.pack(fill='x', pady=2)
        
        self.detection_label = tk.Label(status_frame, text="🛡️ Detection: Active", font=('Arial', 10), bg='#f0f0f0', fg='green', anchor='w')
        self.detection_label.pack(fill='x', pady=2)
        
        # Log
        log_frame = tk.LabelFrame(main_frame, text="📋 Activity Log", font=('Arial', 12, 'bold'), bg='#f0f0f0', padx=15, pady=10)
        log_frame.pack(fill='both', expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap='word', height=12, font=('Courier', 9), bg='#1e1e1e', fg='#00ff00')
        self.log_text.pack(fill='both', expand=True)
    
    def save_api_key(self):
        """Save API key"""
        api_key = self.api_key_entry.get().strip()
        if api_key:
            self.api_handler.save_api_key(api_key)
            messagebox.showinfo("Success", "API key saved!")
        else:
            messagebox.showerror("Error", "Enter API key!")
    
    def log(self, message):
        """Log message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.see('end')
    
    def start_bot(self):
        """Start bot"""
        contact = self.contact_entry.get().strip()
        relation = self.relation_entry.get().strip()
        
        if not contact or not relation:
            messagebox.showerror("Error", "Enter contact and relationship!")
            return
        
        if not self.api_handler.api_key:
            messagebox.showerror("Error", "Enter and save API key first!")
            return
        
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.message_count = 0
        self.conversation_history = []
        
        self.log("🚀 Starting bot with all features...")
        self.log("✅ Detection system: Active")
        self.log("✅ Desktop alerts: Ready")
        self.log("✅ Summary on stop: Enabled")
        self.status_label.config(text="🟢 Status: Running")
        
        self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        self.bot_thread.start()
    
    def stop_bot(self):
        """Stop bot and generate summary"""
        self.log("🛑 Stopping bot...")
        self.log("📊 Generating conversation summary...")
        
        # Generate summary BEFORE stopping
        contact = self.contact_entry.get().strip()
        relation = self.relation_entry.get().strip()
        
        if self.conversation_history:
            summary = self.api_handler.generate_summary(contact, relation, self.conversation_history)
            if summary:
                # Show summary in alert
                self.alerts.show_summary(contact, summary)
                
                # Show in dialog
                self.show_summary_dialog(contact, summary)
        
        self.is_running = False
        
        if self.chrome_manager and self.driver:
            try:
                self.chrome_manager.close_driver(self.driver)
                self.driver = None
            except:
                pass
        
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="⚫ Status: Stopped")
        self.log("✅ Bot stopped")
    
    def show_summary_dialog(self, contact, summary):
        """Show summary in dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"📊 Conversation Summary - {contact}")
        dialog.geometry("600x400")
        dialog.configure(bg='#f0f0f0')
        
        tk.Label(
            dialog,
            text=f"📊 Conversation Summary with {contact}",
            font=('Arial', 14, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=15)
        
        text_widget = scrolledtext.ScrolledText(
            dialog,
            wrap='word',
            height=15,
            font=('Arial', 11),
            bg='white',
            padx=10,
            pady=10
        )
        text_widget.pack(fill='both', expand=True, padx=20, pady=10)
        text_widget.insert('1.0', summary)
        text_widget.config(state='disabled')
        
        tk.Button(
            dialog,
            text="✅ Close",
            command=dialog.destroy,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=30,
            pady=10
        ).pack(pady=15)
    
    def run_bot(self):
        """Main bot loop - USES WORKING CODE + ALL FEATURES"""
        try:
            contact = self.contact_entry.get().strip()
            relation = self.relation_entry.get().strip()
            
            # Initialize (SAME AS WORKING send_message.py)
            self.log("📱 Launching WhatsApp...")
            self.chrome_manager = ChromeManager()
            self.driver = self.chrome_manager.launch_driver('whatsapp')
            self.driver.get(self.chrome_manager.get_whatsapp_url())
            
            self.wa_helper = WhatsAppHelper(self.driver)
            
            if not self.wa_helper.wait_until_loaded():
                self.log("❌ WhatsApp failed to load")
                self.stop_bot()
                return
            
            if not self.wa_helper.open_chat(contact):
                self.log(f"❌ Failed to open chat with {contact}")
                self.stop_bot()
                return
            
            self.log(f"✅ Chat opened with {contact}")
            self.log("🔄 Monitoring with detection enabled...")
            
            # Get initial context
            initial_msgs = self.wa_helper.get_initial_context(10)
            self.conversation_history = initial_msgs
            
            for msg in reversed(initial_msgs):
                if msg.get('sender') == "You":
                    break
                self.last_replied = msg.get('message', '')
            
            # Main loop
            while self.is_running:
                time.sleep(5)
                
                # Get new messages
                new_msgs = self.wa_helper.get_chat_messages(self.last_replied)
                
                if new_msgs:
                    self.last_replied = new_msgs[-1]
                    self.log(f"📥 New: {new_msgs[-1][:50]}...")
                    
                    # Add to history
                    self.conversation_history.append({
                        'sender': contact,
                        'message': new_msgs[-1]
                    })
                    
                    # Generate response WITH DETECTION
                    detection_prompt = self.detection.create_detection_prompt(
                        new_msgs[-1], contact, relation
                    )
                    
                    ai_response = self.api_handler.generate_response(detection_prompt)
                    
                    if ai_response:
                        # CHECK DETECTION
                        check_result = self.detection.check_response(ai_response, new_msgs[-1])
                        
                        if check_result['detected']:
                            # DETECTION ALERT!
                            self.log(f"🚨 DETECTION: {new_msgs[-1]}")
                            self.detection_label.config(text="🚨 Detection: ALERTED!", fg='red')
                            self.alerts.send_detection_alert(contact, new_msgs[-1])
                            # Continue bot (doesn't stop, just alerts)
                            continue
                        
                        # Safe response
                        response = check_result['response']
                        
                        # Typing delay
                        lines = len(response.split('\n'))
                        delay = random.uniform(lines * 1, lines * 2)
                        self.log(f"⌨️ Typing... ({delay:.1f}s)")
                        time.sleep(delay)
                        
                        # Send (WORKING CODE!)
                        if self.wa_helper.send_message(response):
                            self.message_count += 1
                            self.messages_label.config(text=f"💬 Messages: {self.message_count}")
                            self.log(f"✅ Sent: {response[:50]}...")
                            
                            # Add to history
                            self.conversation_history.append({
                                'sender': 'You',
                                'message': response
                            })
                        else:
                            self.log("❌ Send failed")
        
        except Exception as e:
            self.log(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            self.stop_bot()


def main():
    root = tk.Tk()
    app = CompleteWhatsAppBot(root)
    root.mainloop()


if __name__ == "__main__":
    main()
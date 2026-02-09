"""
Auto Form Filler Core - FIXED VERSION
All critical issues resolved:
- Field completion detection
- Shows ALL changes (AI + manual) in review
- Data validation before save
- Backup system
- Improved fuzzy matching
- Clean question text
"""

import json
import os
import sys
import threading
import time
import shutil
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import tkinter as tk
from tkinter import scrolledtext


class AutoFormFillerCore:
    """Core form filler - FIXED VERSION"""
    
    def __init__(self):
        self.data_file = self.get_data_file_path()
        self.user_data = self.load_user_data()
        self.is_active = True
        self.driver = None
        self.monitoring_thread = None
        
        # Change tracking - FIXED: Track both AI and manual
        self.ai_filled_data = {}      # NEW: Track AI auto-fills
        self.manual_changes = {}       # NEW: Track manual changes
        self.current_form_data = {}
        self.monitoring_fields = []
        
        # Multi-page form handling
        self.current_page_url = ""
        self.pages_processed = set()
        
        # Prevent re-filling same form
        self.filled_forms = set()
        
        # Initialize AI Handler
        self.initialize_ai_handler()
    
    def get_data_file_path(self):
        """Get path to user_data.json relative to this script"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, "user_data.json")
    
    def get_api_handler_path(self):
        """Get path to api_handler.py (in parent directory)"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        return parent_dir
    
    def initialize_ai_handler(self):
        """Initialize AI handler from parent directory"""
        try:
            # Add parent directory to path
            api_path = self.get_api_handler_path()
            if api_path not in sys.path:
                sys.path.insert(0, api_path)
            
            from api_handler import APIHandler
            
            # Load config from parent directory
            config_path = os.path.join(api_path, "config.json")
            if os.path.exists(config_path):
                self.ai_handler = APIHandler(config_path=config_path)
                print("✅ AI Handler initialized")
            else:
                print(f"⚠️ config.json not found at: {config_path}")
                self.ai_handler = None
                
        except ImportError as e:
            print(f"⚠️ AI Handler import failed: {e}")
            self.ai_handler = None
        except Exception as e:
            print(f"⚠️ AI Handler init failed: {e}")
            self.ai_handler = None
    
    def load_user_data(self):
        """Load user data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            else:
                default_data = {
                    "personal_info": {},
                    "education": {},
                    "professional": {},
                    "learned_questions": {},
                    "preferences": {
                        "auto_fill_enabled": True,
                        "learn_new_questions": True
                    }
                }
                self.save_user_data(default_data)
                return default_data
        except Exception as e:
            print(f"❌ Error loading user data: {e}")
            return {}
    
    def save_user_data(self, data=None):
        """Save user data to JSON file - FIXED: With backup"""
        if data is None:
            data = self.user_data
        
        try:
            # FIX #1: Create backup before overwriting
            if os.path.exists(self.data_file):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = self.data_file.replace('.json', f'_backup_{timestamp}.json')
                shutil.copy2(self.data_file, backup_file)
                print(f"💾 Backup created: {backup_file}")
                
                # Keep only last 5 backups
                self.cleanup_old_backups(max_backups=5)
            
            # FIX #2: Atomic write (write to temp, then rename)
            temp_file = self.data_file + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Atomic rename (safer than direct write)
            os.replace(temp_file, self.data_file)
            print("✅ Data saved successfully")
            
        except Exception as e:
            print(f"❌ Error saving user data: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def cleanup_old_backups(self, max_backups=5):
        """Keep only the last N backups"""
        try:
            backup_dir = os.path.dirname(self.data_file)
            backup_pattern = os.path.basename(self.data_file).replace('.json', '_backup_')
            
            # Find all backup files
            backups = []
            for file in os.listdir(backup_dir):
                if backup_pattern in file:
                    full_path = os.path.join(backup_dir, file)
                    backups.append((os.path.getmtime(full_path), full_path))
            
            # Sort by modification time (newest first)
            backups.sort(reverse=True)
            
            # Delete old backups
            for _, backup_file in backups[max_backups:]:
                try:
                    os.remove(backup_file)
                    print(f"🗑️ Removed old backup: {backup_file}")
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️ Error cleaning backups: {e}")
    
    def clean_question_text(self, question):
        """FIX: Clean question text before saving"""
        # Remove asterisks for required fields
        question = question.replace('*', '').strip()
        
        # Remove newlines
        question = question.replace('\n', ' ').strip()
        
        # Remove extra whitespace
        question = re.sub(r'\s+', ' ', question)
        
        # Normalize punctuation
        question = question.rstrip('?').rstrip(':').strip()
        
        return question
    
    def monitor_forms(self):
        """Main monitoring loop - 8 Gates System"""
        # Get Chrome config
        chrome_config = self.load_chrome_config()
        if not chrome_config:
            print("❌ Chrome config not found!")
            return
        
        debug_port = chrome_config.get('debug_port', 9222)
        
        # Setup Chrome driver
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print(f"✅ Connected to Chrome on port {debug_port}")
        except Exception as e:
            print(f"❌ Chrome connection failed: {e}")
            print("Make sure Chrome is running with debugging enabled!")
            return
        
        print("\n🔍 Monitoring for Google Forms...")
        
        while self.is_active:
            try:
                current_url = self.driver.current_url
                
                # 🚪 GATE 1: Form Detection
                if "docs.google.com/forms" in current_url and "/viewform" in current_url:
                    
                    # Check if this is a new URL (page change) or first time
                    if current_url != self.current_page_url:
                        print(f"\n🚪 GATE 1: ✅ Form detected (new page)")
                        self.current_page_url = current_url
                        
                        # Process this page (Gates 2-5)
                        self.process_form_page()
                        
                        # Start monitoring for URL change (Submit/Next button)
                        self.wait_for_url_change()
                        
                        # FIXED: Show comprehensive review window
                        print("\n🚪 GATE 7: Opening review window...")
                        user_confirmed = self.show_comprehensive_review_window()
                        
                        # Save data only if user confirmed
                        if user_confirmed:
                            print("\n🚪 GATE 8: Saving to JSON...")
                            self.save_all_changes()
                        else:
                            print("\n🚪 GATE 8: Skipping JSON save (user declined)")
                        
                        # Check if new page has questions or form is complete
                        if self.has_questions_on_page():
                            print("📄 New page detected - processing next page...")
                            # Reset tracking for new page
                            self.ai_filled_data = {}
                            self.manual_changes = {}
                            continue
                        else:
                            print("✅ Form submitted - terminating...")
                            self.cleanup_and_stop()
                            break
                    else:
                        # Same URL, already processed - wait
                        time.sleep(1)
                        continue
                
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                self.cleanup_and_stop()
                break
        
        print("\n🛑 Form filler stopped")
    
    def load_chrome_config(self):
        """Load Chrome configuration"""
        try:
            config_path = os.path.join(self.get_api_handler_path(), "chrome_profile.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('form_filler', {})
            return None
        except Exception as e:
            print(f"❌ Error loading Chrome config: {e}")
            return None
    
    def process_form_page(self):
        """Process current form page - Gates 2-5"""
        try:
            # 🚪 GATE 2: Question Extraction
            print("🚪 GATE 2: Extracting questions...")
            questions_data = self.extract_all_questions()
            
            if not questions_data:
                print("🚪 GATE 2: ❌ No questions found")
                return
            
            print(f"🚪 GATE 2: ✅ Found {len(questions_data)} questions")
            
            # 🚪 GATE 3: Answer Retrieval
            print("🚪 GATE 3: Retrieving answers...")
            answers = self.get_answers_for_questions(questions_data)
            print(f"🚪 GATE 3: ✅ Retrieved {len(answers)} answers")
            
            # 🚪 GATE 4: Form Filling
            print("🚪 GATE 4: Filling form...")
            filled_count = self.fill_form_with_answers(questions_data, answers)
            print(f"🚪 GATE 4: ✅ Filled {filled_count} fields")
            
            # 🚪 GATE 5: Change Monitoring
            print("🚪 GATE 5: Starting change monitoring...")
            self.start_change_monitoring(questions_data)
            print("🚪 GATE 5: ✅ Monitoring active")
            
        except Exception as e:
            print(f"❌ Page processing error: {e}")
    
    def extract_all_questions(self):
        """Extract all questions from current page"""
        questions_data = []
        
        try:
            # Wait for form to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='listitem'], [data-params]"))
            )
            
            # Try multiple selectors
            selectors = [
                "[role='listitem']",
                "[data-params]",
                ".freebirdFormviewerViewNumberedItemContainer"
            ]
            
            questions = []
            for selector in selectors:
                try:
                    questions = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if questions:
                        break
                except:
                    continue
            
            if not questions:
                return []
            
            for i, question_elem in enumerate(questions):
                try:
                    # Extract question text
                    question_text = self.extract_question_text(question_elem)
                    if not question_text:
                        continue
                    
                    # FIX: Clean question text
                    question_text = self.clean_question_text(question_text)
                    
                    # Extract fields
                    fields = self.extract_fields(question_elem)
                    if not fields:
                        continue
                    
                    questions_data.append({
                        'question': question_text,
                        'element': question_elem,
                        'fields': fields,
                        'index': i
                    })
                    
                except Exception as e:
                    continue
            
            return questions_data
            
        except Exception as e:
            print(f"Question extraction failed: {e}")
            return []
    
    def extract_question_text(self, element):
        """Extract question text from element"""
        try:
            selectors = [
                "[role='heading']",
                ".freebirdFormviewerComponentsQuestionBaseTitle",
                ".freebirdFormviewerComponentsQuestionBaseHeader"
            ]
            
            for selector in selectors:
                try:
                    text_elem = element.find_element(By.CSS_SELECTOR, selector)
                    text = text_elem.text.strip()
                    if text:
                        return text
                except:
                    continue
            
            # Fallback
            return element.text.strip().split('\n')[0] if element.text else ""
            
        except:
            return ""
    
    def extract_fields(self, element):
        """Extract all input fields from question element"""
        fields = {
            'text': [],
            'radio': [],
            'checkbox': [],
            'select': [],
            'textarea': []
        }
        
        try:
            # Text inputs
            text_inputs = element.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email'], input[type='tel'], input[type='number']")
            fields['text'] = text_inputs
            
            # Radio buttons
            radios = element.find_elements(By.CSS_SELECTOR, "[role='radio'], input[type='radio']")
            fields['radio'] = radios
            
            # Checkboxes
            checkboxes = element.find_elements(By.CSS_SELECTOR, "[role='checkbox'], input[type='checkbox']")
            fields['checkbox'] = checkboxes
            
            # Textareas
            textareas = element.find_elements(By.TAG_NAME, "textarea")
            fields['textarea'] = textareas
            
            # Selects/Dropdowns
            selects = element.find_elements(By.TAG_NAME, "select")
            fields['select'] = selects
            
        except Exception as e:
            pass
        
        return fields
    
    def get_answers_for_questions(self, questions_data):
        """Get answers using 3-level system: JSON exact → JSON fuzzy → AI batch"""
        answers = {}
        unanswered_questions = []
        
        # Level 1 & 2: JSON matching
        for q_data in questions_data:
            question = q_data['question']
            
            # Level 1: Exact match
            if question in self.user_data.get("learned_questions", {}):
                answers[question] = self.user_data["learned_questions"][question]
                continue
            
            # Level 2: Fuzzy match (FIXED: Better threshold)
            fuzzy_answer = self.fuzzy_match_json(question)
            if fuzzy_answer:
                answers[question] = fuzzy_answer
                continue
            
            # Collect for AI
            unanswered_questions.append(question)
        
        # Level 3: AI batch processing (FIXED: Don't save immediately)
        if unanswered_questions and self.ai_handler:
            print(f"🤖 Batch AI call for {len(unanswered_questions)} questions...")
            batch_answers = self.ask_ai_batch(unanswered_questions)
            answers.update(batch_answers)
            
            # FIXED: Store AI answers separately for review, don't save yet
            for question, answer in batch_answers.items():
                if answer and "DATA_NOT_AVAILABLE" not in answer:
                    # Mark as AI-generated (will be reviewed before saving)
                    self.ai_filled_data[question] = {
                        'answer': answer,
                        'source': 'AI',
                        'needs_review': True
                    }
                    print(f"🤖 AI suggested: {question} → {answer}")
        
        # Fill remaining with None
        for question in unanswered_questions:
            if question not in answers:
                answers[question] = None
        
        return answers
    
    def fuzzy_match_json(self, question):
        """FIX: Improved fuzzy match with higher threshold"""
        question_lower = question.lower()
        
        # Check learned questions
        for saved_q, answer in self.user_data.get("learned_questions", {}).items():
            if self.is_similar_question(question_lower, saved_q.lower()):
                return answer
        
        # Check personal info patterns
        patterns = {
            'full_name': ['full name', 'complete name', 'your name'],
            'first_name': ['first name', 'given name'],
            'last_name': ['last name', 'surname', 'family name'],
            'email': ['email address', 'email', 'e-mail'],
            'phone': ['phone number', 'mobile number', 'contact number'],
            'address': ['address', 'street address'],
            'city': ['city', 'town'],
            'state': ['state', 'province'],
            'country': ['country', 'nation'],
            'zip_code': ['zip code', 'postal code', 'pin code']
        }
        
        for key, keywords in patterns.items():
            if any(kw == question_lower or question_lower.startswith(kw) for kw in keywords):
                value = self.user_data.get("personal_info", {}).get(key)
                if value:
                    return value
        
        return None
    
    def is_similar_question(self, q1, q2, threshold=0.75):
        """FIX: Better similarity with higher threshold and key word checking"""
        
        # Remove common stop words
        stop_words = {'what', 'is', 'your', 'the', 'a', 'an', 'are', 'you', 'my', 'enter'}
        words1 = set(q1.split()) - stop_words
        words2 = set(q2.split()) - stop_words
        
        if not words1 or not words2:
            return False
        
        common = words1.intersection(words2)
        
        # FIXED: Higher threshold (75% instead of 50%)
        similarity = len(common) / max(len(words1), len(words2))
        
        if similarity < threshold:
            return False
        
        # FIXED: Additional check for key differentiating words
        key_indicators = {
            'mother', 'father', 'parent', 'emergency', 'current', 'previous',
            'dream', 'favorite', 'home', 'work', 'school', 'primary', 'alternate'
        }
        
        key_words_1 = words1.intersection(key_indicators)
        key_words_2 = words2.intersection(key_indicators)
        
        # If either has key words, they MUST match exactly
        if (key_words_1 or key_words_2) and key_words_1 != key_words_2:
            return False
        
        return True
    
    def validate_answer(self, question, answer):
        """FIX: Validate answer before saving"""
        issues = []
        question_lower = question.lower()
        
        # Check for truncation (too short)
        if len(answer) < 2:
            issues.append("Answer seems too short")
        
        # Name validation
        if 'name' in question_lower and 'user' not in question_lower:
            # Full name should have at least 2 words
            if 'full' in question_lower or 'complete' in question_lower:
                if len(answer.split()) < 2:
                    issues.append("Full name should have first and last name")
        
        # Email validation
        if 'email' in question_lower or 'e-mail' in question_lower:
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', answer):
                issues.append("Email format appears invalid")
        
        # Phone validation
        if 'phone' in question_lower or 'mobile' in question_lower:
            digits = re.sub(r'\D', '', answer)
            if len(digits) < 10:
                issues.append("Phone number seems too short")
        
        return len(issues) == 0, issues
    
    def ask_ai_batch(self, questions):
        """Ask AI to answer multiple questions in one batch call"""
        try:
            json_context = json.dumps(self.user_data, indent=2)
            questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
            
            prompt = f"""You are a form-filling assistant. Based on the user's profile data, answer ALL these questions.

USER PROFILE DATA:
{json_context}

QUESTIONS:
{questions_text}

INSTRUCTIONS:
1. Look through ALL sections of the profile data
2. For each question, if you find relevant information, provide ONLY the answer value
3. If NO relevant information exists for a question, respond EXACTLY with: DATA_NOT_AVAILABLE
4. Use semantic matching (e.g., "Student Name" can use "full_name")
5. DO NOT make assumptions or guess
6. DO NOT hallucinate data
7. Return answers in this exact format:
Q1: [answer to question 1]
Q2: [answer to question 2]
Q3: [answer to question 3]
etc.

Answers:"""

            result = self.ai_handler.send_request(prompt)
            
            if isinstance(result, dict) and result.get('success'):
                response = result['response'].strip()
                return self.parse_batch_ai_response(response, questions)
            elif isinstance(result, str):
                return self.parse_batch_ai_response(result, questions)
            else:
                print(f"❌ Unexpected AI response format: {type(result)}")
                return {}
                
        except Exception as e:
            print(f"❌ Batch AI error: {e}")
            return {}
    
    def parse_batch_ai_response(self, response, questions):
        """Parse AI batch response into individual answers"""
        answers = {}
        
        try:
            lines = response.strip().split('\n')
            for i, line in enumerate(lines):
                if f"Q{i+1}:" in line:
                    answer = line.split(f"Q{i+1}:")[1].strip()
                    if answer and "DATA_NOT_AVAILABLE" not in answer:
                        answers[questions[i]] = answer
                        print(f"✅ AI answered Q{i+1}: {answer}")
                    else:
                        print(f"❌ AI has no data for Q{i+1}")
        except Exception as e:
            print(f"❌ Error parsing AI response: {e}")
        
        return answers
    
    def fill_form_with_answers(self, questions_data, answers):
        """Fill form with retrieved answers"""
        filled_count = 0
        
        for q_data in questions_data:
            question = q_data['question']
            answer = answers.get(question)
            
            if not answer:
                continue
            
            fields = q_data['fields']
            
            # Fill based on field type
            if fields['text']:
                if self.fill_text_field(fields['text'][0], answer):
                    self.current_form_data[question] = {'value': answer, 'type': 'text'}
                    filled_count += 1
            
            elif fields['textarea']:
                if self.fill_text_field(fields['textarea'][0], answer):
                    self.current_form_data[question] = {'value': answer, 'type': 'textarea'}
                    filled_count += 1
            
            elif fields['radio']:
                if self.fill_radio_field(fields['radio'], answer):
                    self.current_form_data[question] = {'value': answer, 'type': 'radio'}
                    filled_count += 1
            
            elif fields['checkbox']:
                if self.fill_checkbox_field(fields['checkbox'], answer):
                    self.current_form_data[question] = {'value': answer, 'type': 'checkbox'}
                    filled_count += 1
            
            elif fields['select']:
                if self.fill_select_field(fields['select'][0], answer):
                    self.current_form_data[question] = {'value': answer, 'type': 'select'}
                    filled_count += 1
        
        return filled_count
    
    def fill_text_field(self, field, answer):
        """Fill text input or textarea"""
        try:
            field.clear()
            field.send_keys(str(answer))
            return True
        except:
            return False
    
    def fill_radio_field(self, radios, answer):
        """Fill radio button"""
        try:
            answer_lower = str(answer).lower()
            for radio in radios:
                label = radio.get_attribute('aria-label') or radio.text or ""
                if answer_lower in label.lower():
                    radio.click()
                    return True
            return False
        except:
            return False
    
    def fill_checkbox_field(self, checkboxes, answer):
        """Fill checkbox"""
        try:
            answer_lower = str(answer).lower()
            for checkbox in checkboxes:
                label = checkbox.get_attribute('aria-label') or checkbox.text or ""
                if answer_lower in label.lower():
                    if not checkbox.is_selected():
                        checkbox.click()
                    return True
            return False
        except:
            return False
    
    def fill_select_field(self, select, answer):
        """Fill select dropdown"""
        try:
            answer_lower = str(answer).lower()
            options = select.find_elements(By.TAG_NAME, "option")
            for option in options:
                if answer_lower in option.text.lower():
                    option.click()
                    return True
            return False
        except:
            return False
    
    def start_change_monitoring(self, questions_data):
        """FIX: Monitor changes with field completion detection"""
        monitoring = True
        initial_values = {}
        field_stable_count = {}  # NEW: Track stability
        
        # Store initial values
        for q_data in questions_data:
            question = q_data['question']
            fields = q_data['fields']
            current_value = self.get_current_value(fields)
            initial_values[question] = current_value
            field_stable_count[question] = 0
        
        def monitor():
            while monitoring:
                time.sleep(0.5)
                
                for q_data in questions_data:
                    if not monitoring:
                        break
                    
                    question = q_data['question']
                    fields = q_data['fields']
                    
                    try:
                        current_value = self.get_current_value(fields)
                        initial_value = initial_values.get(question, '')
                        
                        # FIX: Check if value changed
                        if current_value != initial_value:
                            # FIX: Wait for field to stabilize before recording
                            if question in field_stable_count:
                                field_stable_count[question] += 1
                            else:
                                field_stable_count[question] = 1
                            
                            # FIX: Only record after 3 stable checks (1.5 seconds)
                            if field_stable_count[question] >= 3:
                                # FIX: Validate before recording
                                is_valid, issues = self.validate_answer(question, current_value)
                                
                                if is_valid:
                                    field_type = self.get_field_type(fields)
                                    self.manual_changes[question] = {
                                        'original': initial_value,
                                        'new': current_value,
                                        'type': field_type
                                    }
                                else:
                                    print(f"⚠️ Validation issues for '{question}': {', '.join(issues)}")
                        else:
                            # Reset stability counter if value matches initial
                            field_stable_count[question] = 0
                            
                    except Exception as e:
                        pass
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def get_current_value(self, fields):
        """Get current value from fields"""
        try:
            if fields['text']:
                return fields['text'][0].get_attribute('value') or ''
            if fields['textarea']:
                return fields['textarea'][0].get_attribute('value') or fields['textarea'][0].text or ''
            if fields['select']:
                try:
                    selected = fields['select'][0].find_element(By.CSS_SELECTOR, "option:checked")
                    return selected.text.strip()
                except:
                    return ''
        except:
            pass
        
        return ''
    
    def get_field_type(self, fields):
        """Get field type"""
        if fields['text']: return 'text'
        if fields['textarea']: return 'textarea'
        if fields['radio']: return 'radio'
        if fields['checkbox']: return 'checkbox'
        if fields['select']: return 'select'
        return 'unknown'
    
    def wait_for_url_change(self):
        """Wait for URL to change (Submit/Next button clicked)"""
        print("\n🚪 GATE 6: ⏳ Waiting for Submit/Next button click...")
        
        original_url = self.driver.current_url
        
        while self.is_active:
            time.sleep(0.5)
            current_url = self.driver.current_url
            
            if current_url != original_url:
                print("🚪 GATE 6: ✅ URL changed - form page submitted/advanced")
                return
        
        print("🚪 GATE 6: ⚠️ Stopped before URL change")
    
    def has_questions_on_page(self):
        """Check if current page has questions"""
        try:
            time.sleep(1)  # Wait for page load
            
            # Try to find question elements
            selectors = [
                "[role='listitem']",
                "[data-params]",
                ".freebirdFormviewerViewNumberedItemContainer"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and len(elements) > 0:
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"❌ Error checking for questions: {e}")
            return False
    
    def show_comprehensive_review_window(self):
        """FIX: Show ALL changes (AI + manual) for user review"""
        # Create root window if it doesn't exist
        root = tk.Tk()
        root.withdraw()  # Hide root window
        
        review_window = tk.Toplevel(root)
        review_window.title("📝 Form Page Review - ALL CHANGES")
        review_window.geometry("700x600")
        review_window.attributes('-topmost', True)
        
        # Header
        header = tk.Label(review_window, text="📝 Complete Form Review", 
                         font=("Arial", 14, "bold"), pady=10)
        header.pack()
        
        # Note
        note = tk.Label(review_window, 
                       text="⚠️ Review ALL changes below before saving to your profile.\n" +
                            "🤖 = AI auto-filled | ✏️ = You manually changed", 
                       font=("Arial", 10), fg="blue", justify="left")
        note.pack()
        
        # Scrollable text widget
        text_widget = scrolledtext.ScrolledText(review_window, wrap='word', height=20)
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Configure tags for coloring
        text_widget.tag_config('ai_tag', foreground='purple', font=('Arial', 10, 'bold'))
        text_widget.tag_config('manual_tag', foreground='green', font=('Arial', 10, 'bold'))
        text_widget.tag_config('warning_tag', foreground='red')
        
        # Display AI-filled data
        if self.ai_filled_data:
            text_widget.insert('end', f"🤖 AI AUTO-FILLED ({len(self.ai_filled_data)} fields):\n", 'ai_tag')
            text_widget.insert('end', "="*60 + "\n\n")
            
            for i, (question, data) in enumerate(self.ai_filled_data.items(), 1):
                answer = data['answer']
                
                # Validate
                is_valid, issues = self.validate_answer(question, answer)
                
                text_widget.insert('end', f"{i}. {question}\n")
                text_widget.insert('end', f"   Answer: {answer}\n")
                
                if not is_valid:
                    text_widget.insert('end', f"   ⚠️ Issues: {', '.join(issues)}\n", 'warning_tag')
                
                text_widget.insert('end', "-"*60 + "\n\n")
        
        # Display manual changes
        if self.manual_changes:
            text_widget.insert('end', f"\n✏️ YOUR MANUAL CHANGES ({len(self.manual_changes)} fields):\n", 'manual_tag')
            text_widget.insert('end', "="*60 + "\n\n")
            
            for i, (question, change_data) in enumerate(self.manual_changes.items(), 1):
                text_widget.insert('end', f"{i}. {question}\n")
                text_widget.insert('end', f"   Original: {change_data['original']}\n")
                text_widget.insert('end', f"   Changed to: {change_data['new']}\n")
                text_widget.insert('end', f"   Type: {change_data['type']}\n")
                text_widget.insert('end', "-"*60 + "\n\n")
        
        if not self.ai_filled_data and not self.manual_changes:
            text_widget.insert('end', "ℹ️ No changes detected on this page.\n")
        
        text_widget.config(state='disabled')
        
        # Result variable
        user_choice = {'confirmed': False}
        
        def confirm_save():
            user_choice['confirmed'] = True
            review_window.destroy()
            root.quit()
        
        def cancel_save():
            user_choice['confirmed'] = False
            review_window.destroy()
            root.quit()
        
        # Buttons
        button_frame = tk.Frame(review_window)
        button_frame.pack(pady=10)
        
        ok_button = tk.Button(button_frame, text="✅ OK - Save All to Profile", 
                             command=confirm_save,
                             bg="#4CAF50", fg="white", padx=20, pady=8, font=("Arial", 11, "bold"))
        ok_button.pack(side="left", padx=5)
        
        cancel_button = tk.Button(button_frame, text="❌ Cancel - Don't Save", 
                                command=cancel_save,
                                bg="#f44336", fg="white", padx=20, pady=8, font=("Arial", 11, "bold"))
        cancel_button.pack(side="left", padx=5)
        
        total_changes = len(self.ai_filled_data) + len(self.manual_changes)
        print(f"🚪 GATE 7: ✅ Review window shown ({total_changes} total changes)")
        
        # Wait for window to close
        root.mainloop()
        root.destroy()
        
        return user_choice['confirmed']
    
    def save_all_changes(self):
        """FIX: Save both AI and manual changes after user confirmation"""
        try:
            saved_count = 0
            
            # Save AI-filled data
            for question, data in self.ai_filled_data.items():
                answer = data['answer']
                if answer and answer.strip():
                    # Validate before saving
                    is_valid, issues = self.validate_answer(question, answer)
                    
                    if is_valid:
                        if "learned_questions" not in self.user_data:
                            self.user_data["learned_questions"] = {}
                        
                        # Clean question before saving
                        clean_q = self.clean_question_text(question)
                        self.user_data["learned_questions"][clean_q] = answer
                        saved_count += 1
                        print(f"💾 Saved AI answer: {clean_q} → {answer}")
                    else:
                        print(f"⚠️ Skipped invalid AI answer for '{question}': {', '.join(issues)}")
            
            # Save manual changes
            for question, change_data in self.manual_changes.items():
                new_value = change_data['new']
                if new_value and new_value.strip():
                    # Validate before saving
                    is_valid, issues = self.validate_answer(question, new_value)
                    
                    if is_valid:
                        if "learned_questions" not in self.user_data:
                            self.user_data["learned_questions"] = {}
                        
                        # Clean question before saving
                        clean_q = self.clean_question_text(question)
                        self.user_data["learned_questions"][clean_q] = new_value
                        saved_count += 1
                        print(f"💾 Saved manual change: {clean_q} → {new_value}")
                    else:
                        print(f"⚠️ Skipped invalid manual change for '{question}': {', '.join(issues)}")
            
            if saved_count > 0:
                self.save_user_data()
                print(f"🚪 GATE 8: ✅ Saved {saved_count} items to JSON")
            else:
                print("🚪 GATE 8: ⚠️ No new data to save")
            
            # Clear tracking for next page
            self.ai_filled_data = {}
            self.manual_changes = {}
            
        except Exception as e:
            print(f"❌ Error saving changes: {e}")
    
    def cleanup_and_stop(self):
        """Cleanup and stop"""
        self.is_active = False
        self.ai_filled_data = {}
        self.manual_changes = {}
        self.current_form_data = {}
        self.pages_processed = set()
        self.current_page_url = ""
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        print("🔴 Auto Form Filler: STOPPED")
    
    def run(self):
        """Run the form filler"""
        print("\n" + "="*60)
        print("🤖 AUTO FORM FILLER CORE - FIXED VERSION - Started!")
        print("="*60)
        if self.ai_handler:
            print("✅ AI Handler: Active")
        else:
            print("⚠️ AI Handler: Disabled")
        print("="*60 + "\n")
        
        self.monitor_forms()


if __name__ == "__main__":
    filler = AutoFormFillerCore()
    filler.run()
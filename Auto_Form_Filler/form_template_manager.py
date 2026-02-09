"""
Form Filler Template Manager - Phase 7
Manages multiple form templates for different sites
Provides template export/import and quick-fill functionality
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class FormTemplateManager:
    """
    Manages form templates for multi-site support
    
    Features:
    - Save form templates for specific sites
    - Import/export templates
    - Quick-fill from templates
    - Template library management
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize template manager
        
        Args:
            templates_dir: Directory for template storage
        """
        if templates_dir is None:
            # Default to Auto_Form_Filler/templates directory
            self.templates_dir = Path(__file__).parent / "templates"
        else:
            self.templates_dir = Path(templates_dir)
        
        # Create templates directory if it doesn't exist
        self.templates_dir.mkdir(exist_ok=True)
        
        self.templates = self._load_all_templates()
    
    def _load_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load all templates from directory"""
        templates = {}
        
        if not self.templates_dir.exists():
            return templates
        
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    template_data = json.load(f)
                    template_name = template_file.stem
                    templates[template_name] = template_data
            except Exception as e:
                print(f"Warning: Failed to load template {template_file}: {e}")
        
        return templates
    
    def create_template(
        self,
        name: str,
        site_url: str,
        field_mappings: Dict[str, str],
        description: str = ""
    ) -> bool:
        """
        Create a new form template
        
        Args:
            name: Template name (used as filename)
            site_url: Website URL or pattern
            field_mappings: Dict mapping field labels to user_data keys
            description: Template description
            
        Returns:
            True if created successfully
        """
        template = {
            "name": name,
            "site_url": site_url,
            "description": description,
            "field_mappings": field_mappings,
            "created_at": datetime.now().isoformat(),
            "last_used": None,
            "use_count": 0
        }
        
        # Save template
        template_path = self.templates_dir / f"{name}.json"
        
        try:
            with open(template_path, 'w') as f:
                json.dump(template, f, indent=2)
            
            self.templates[name] = template
            print(f"✅ Template '{name}' created successfully")
            return True
        
        except Exception as e:
            print(f"❌ Failed to create template: {e}")
            return False
    
    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Get template by name"""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List all available template names"""
        return list(self.templates.keys())
    
    def get_template_for_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Find template matching a URL
        
        Args:
            url: Current form URL
            
        Returns:
            Matching template or None
        """
        for name, template in self.templates.items():
            site_url = template.get('site_url', '')
            
            # Simple pattern matching
            if site_url in url or url in site_url:
                return template
        
        return None
    
    def update_template_usage(self, name: str):
        """Update template usage statistics"""
        if name in self.templates:
            template = self.templates[name]
            template['last_used'] = datetime.now().isoformat()
            template['use_count'] = template.get('use_count', 0) + 1
            
            # Save updated template
            template_path = self.templates_dir / f"{name}.json"
            try:
                with open(template_path, 'w') as f:
                    json.dump(template, f, indent=2)
            except Exception as e:
                print(f"Warning: Failed to update template usage: {e}")
    
    def delete_template(self, name: str) -> bool:
        """Delete a template"""
        if name not in self.templates:
            return False
        
        template_path = self.templates_dir / f"{name}.json"
        
        try:
            template_path.unlink()
            del self.templates[name]
            print(f"✅ Template '{name}' deleted")
            return True
        except Exception as e:
            print(f"❌ Failed to delete template: {e}")
            return False
    
    def export_template(self, name: str, export_path: Path) -> bool:
        """Export template to a file"""
        if name not in self.templates:
            print(f"❌ Template '{name}' not found")
            return False
        
        try:
            import shutil
            source = self.templates_dir / f"{name}.json"
            shutil.copy(source, export_path)
            print(f"✅ Template exported to: {export_path}")
            return True
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
    
    def import_template(self, template_path: Path) -> bool:
        """Import template from a file"""
        try:
            with open(template_path, 'r') as f:
                template_data = json.load(f)
            
            name = template_data.get('name', template_path.stem)
            
            # Save to templates directory
            dest_path = self.templates_dir / f"{name}.json"
            
            with open(dest_path, 'w') as f:
                json.dump(template_data, f, indent=2)
            
            self.templates[name] = template_data
            print(f"✅ Template '{name}' imported successfully")
            return True
        
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return False
    
    def get_template_info(self, name: str) -> Optional[str]:
        """Get formatted information about a template"""
        template = self.get_template(name)
        
        if not template:
            return None
        
        info = f"""
Template: {template['name']}
Site: {template['site_url']}
Description: {template.get('description', 'N/A')}
Fields: {len(template['field_mappings'])} mapped
Created: {template['created_at'][:10]}
Last Used: {template.get('last_used', 'Never')[:10] if template.get('last_used') else 'Never'}
Usage Count: {template.get('use_count', 0)}
"""
        return info


class AIFieldDetector:
    """
    AI-powered field detection and mapping
    
    Uses AI to intelligently detect form field purposes
    and suggest appropriate mappings from user data
    """
    
    def __init__(self, ai_handler=None):
        """
        Initialize AI field detector
        
        Args:
            ai_handler: APIHandler instance for AI requests
        """
        self.ai_handler = ai_handler
    
    def detect_field_purpose(
        self,
        field_label: str,
        field_type: str,
        field_id: str = "",
        field_name: str = ""
    ) -> Dict[str, Any]:
        """
        Detect the purpose of a form field using AI
        
        Args:
            field_label: Label text of the field
            field_type: Input type (text, email, tel, etc.)
            field_id: Field ID attribute
            field_name: Field name attribute
            
        Returns:
            Dict with detected purpose and suggested mapping
        """
        if not self.ai_handler:
            return self._fallback_detection(field_label, field_type)
        
        try:
            prompt = f"""Analyze this form field and determine what information it's asking for:

Field Label: "{field_label}"
Input Type: {field_type}
Field ID: {field_id}
Field Name: {field_name}

Common categories:
- personal: name, email, phone, address, date_of_birth, gender
- education: school, degree, graduation_year, major, gpa
- professional: job_title, company, experience, skills, resume
- other: custom fields

Respond with ONLY a JSON object:
{{"category": "personal|education|professional|other", "field_type": "specific_type", "confidence": 0.0-1.0}}

Examples:
"Full Name" → {{"category": "personal", "field_type": "full_name", "confidence": 0.95}}
"Email Address" → {{"category": "personal", "field_type": "email", "confidence": 1.0}}
"University" → {{"category": "education", "field_type": "school", "confidence": 0.9}}
"""
            
            response = self.ai_handler.send_request(prompt)
            
            # Parse AI response
            if isinstance(response, dict):
                return response
            elif isinstance(response, str):
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
            
            return self._fallback_detection(field_label, field_type)
        
        except Exception as e:
            print(f"AI detection failed: {e}")
            return self._fallback_detection(field_label, field_type)
    
    def _fallback_detection(self, field_label: str, field_type: str) -> Dict[str, Any]:
        """Fallback pattern-based detection"""
        label_lower = field_label.lower()
        
        # Pattern matching
        patterns = {
            'full_name': ['full name', 'name', 'your name'],
            'first_name': ['first name', 'fname', 'given name'],
            'last_name': ['last name', 'lname', 'surname', 'family name'],
            'email': ['email', 'e-mail', 'email address'],
            'phone': ['phone', 'mobile', 'telephone', 'contact number'],
            'address': ['address', 'street', 'location'],
            'city': ['city', 'town'],
            'state': ['state', 'province', 'region'],
            'zip': ['zip', 'postal', 'pincode'],
            'country': ['country', 'nation'],
            'date_of_birth': ['birth', 'dob', 'birthday'],
            'gender': ['gender', 'sex'],
            'school': ['school', 'university', 'college', 'institution'],
            'degree': ['degree', 'qualification', 'education level'],
            'major': ['major', 'field of study', 'specialization'],
            'job_title': ['job title', 'position', 'role', 'occupation'],
            'company': ['company', 'organization', 'employer'],
        }
        
        for field_type_key, keywords in patterns.items():
            if any(keyword in label_lower for keyword in keywords):
                category = self._get_category(field_type_key)
                return {
                    "category": category,
                    "field_type": field_type_key,
                    "confidence": 0.7
                }
        
        return {
            "category": "other",
            "field_type": "unknown",
            "confidence": 0.3
        }
    
    def _get_category(self, field_type: str) -> str:
        """Get category for a field type"""
        personal_fields = ['full_name', 'first_name', 'last_name', 'email', 
                          'phone', 'address', 'city', 'state', 'zip', 'country',
                          'date_of_birth', 'gender']
        
        education_fields = ['school', 'degree', 'major', 'graduation_year', 'gpa']
        
        professional_fields = ['job_title', 'company', 'experience', 'skills', 'resume']
        
        if field_type in personal_fields:
            return 'personal'
        elif field_type in education_fields:
            return 'education'
        elif field_type in professional_fields:
            return 'professional'
        else:
            return 'other'
    
    def suggest_mappings(self, form_fields: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Suggest field mappings for an entire form
        
        Args:
            form_fields: List of field dicts with label, type, id, name
            
        Returns:
            Dict mapping field labels to suggested user_data keys
        """
        mappings = {}
        
        for field in form_fields:
            label = field.get('label', '')
            field_type = field.get('type', 'text')
            field_id = field.get('id', '')
            field_name = field.get('name', '')
            
            detection = self.detect_field_purpose(label, field_type, field_id, field_name)
            
            if detection['confidence'] > 0.5:
                # Build user_data key path
                category = detection['category']
                field_type_key = detection['field_type']
                
                if category != 'other':
                    user_data_key = f"{category}.{field_type_key}"
                    mappings[label] = user_data_key
        
        return mappings


# Default templates for common sites
DEFAULT_TEMPLATES = {
    "google_forms": {
        "name": "google_forms",
        "site_url": "docs.google.com/forms",
        "description": "Standard Google Forms template",
        "field_mappings": {
            "Name": "personal_info.full_name",
            "Email": "personal_info.email",
            "Phone": "personal_info.phone",
            "Address": "personal_info.address",
        },
        "created_at": "2024-01-01T00:00:00",
        "last_used": None,
        "use_count": 0
    },
    "job_application": {
        "name": "job_application",
        "site_url": "careers",
        "description": "Common job application form fields",
        "field_mappings": {
            "Full Name": "personal_info.full_name",
            "Email Address": "personal_info.email",
            "Phone Number": "personal_info.phone",
            "Current Position": "professional.job_title",
            "Current Company": "professional.company",
            "Years of Experience": "professional.experience",
            "LinkedIn": "professional.linkedin",
            "Resume": "professional.resume_path",
        },
        "created_at": "2024-01-01T00:00:00",
        "last_used": None,
        "use_count": 0
    }
}


def initialize_default_templates(templates_dir: Path):
    """Initialize default templates if they don't exist"""
    templates_dir.mkdir(exist_ok=True)
    
    for template_name, template_data in DEFAULT_TEMPLATES.items():
        template_path = templates_dir / f"{template_name}.json"
        
        if not template_path.exists():
            try:
                with open(template_path, 'w') as f:
                    json.dump(template_data, f, indent=2)
                print(f"✅ Created default template: {template_name}")
            except Exception as e:
                print(f"⚠️  Failed to create template {template_name}: {e}")

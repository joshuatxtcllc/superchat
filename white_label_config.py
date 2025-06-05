
"""
White Label Configuration System
Allows easy customization of branding, features, and deployment
"""

import os
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any

@dataclass
class BrandingConfig:
    """Branding configuration for white-label deployment"""
    
    # Company Information
    company_name: str = "Multi-Model Chat Interface"
    company_logo_url: str = ""
    company_website: str = ""
    company_support_email: str = ""
    
    # App Branding
    app_title: str = "Multi-Model Chat Interface"
    app_description: str = "Interact with multiple AI models in one unified experience"
    app_icon: str = "💬"
    app_tagline: str = "Powered by Model Context Protocol"
    
    # Color Scheme
    primary_color: str = "#2D87D3"
    secondary_color: str = "#36a9e1"
    background_color: str = "#f8f9fa"
    accent_color: str = "#f0f7ff"
    text_color: str = "#333"
    
    # Footer
    show_powered_by: bool = True
    custom_footer_text: str = ""
    copyright_text: str = "© 2025 · All Rights Reserved"
    
    # Custom CSS Override
    custom_css: str = ""

@dataclass
class FeatureConfig:
    """Feature configuration for white-label deployment"""
    
    # Core Features
    enable_model_comparison: bool = True
    enable_conversation_starters: bool = True
    enable_model_recommender: bool = True
    enable_deep_thinking: bool = True
    enable_image_generation: bool = True
    enable_file_upload: bool = True
    enable_screen_sharing: bool = True
    enable_mcp: bool = True
    
    # Available Models (can be restricted per deployment)
    allowed_models: List[str] = None  # None means all models
    default_model: str = "gpt-4o"
    
    # UI Features
    enable_export_conversation: bool = True
    enable_copy_conversation: bool = True
    enable_conversation_history: bool = True
    show_model_info: bool = True
    show_api_status: bool = True
    
    # Rate Limiting
    max_messages_per_session: int = 20
    min_time_between_messages: float = 2.0
    max_message_length: int = 10000
    
    # Custom Conversation Starters
    custom_conversation_starters: Dict[str, List[str]] = None

@dataclass
class DeploymentConfig:
    """Deployment-specific configuration"""
    
    # API Keys (environment variables)
    required_api_keys: List[str] = None
    
    # Analytics
    enable_analytics: bool = False
    analytics_tracking_id: str = ""
    
    # Custom Domains
    custom_domain: str = ""
    
    # Security
    enable_authentication: bool = False
    allowed_users: List[str] = None
    
    # Limits
    daily_message_limit: int = 100
    monthly_usage_limit: int = 1000

class WhiteLabelConfig:
    """Main white-label configuration manager"""
    
    def __init__(self, config_file: str = "white_label_config.json"):
        self.config_file = config_file
        self.branding = BrandingConfig()
        self.features = FeatureConfig()
        self.deployment = DeploymentConfig()
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    
                    # Load branding config
                    if 'branding' in config_data:
                        for key, value in config_data['branding'].items():
                            if hasattr(self.branding, key):
                                setattr(self.branding, key, value)
                    
                    # Load features config
                    if 'features' in config_data:
                        for key, value in config_data['features'].items():
                            if hasattr(self.features, key):
                                setattr(self.features, key, value)
                    
                    # Load deployment config
                    if 'deployment' in config_data:
                        for key, value in config_data['deployment'].items():
                            if hasattr(self.deployment, key):
                                setattr(self.deployment, key, value)
        
        except Exception as e:
            print(f"Error loading white-label config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config_data = {
                'branding': asdict(self.branding),
                'features': asdict(self.features),
                'deployment': asdict(self.deployment)
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving white-label config: {e}")
            return False
    
    def get_custom_css(self) -> str:
        """Generate custom CSS based on branding configuration"""
        base_css = f"""
        <style>
            :root {{
                --primary-color: {self.branding.primary_color};
                --secondary-color: {self.branding.secondary_color};
                --background-color: {self.branding.background_color};
                --accent-color: {self.branding.accent_color};
                --text-color: {self.branding.text_color};
            }}
            
            .main {{
                padding: 0 1rem;
                max-width: 65rem;
                margin: 0 auto;
                background-color: var(--background-color);
                color: var(--text-color);
            }}
            
            /* Custom branded styling */
            h1, .brand-title {{
                background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 700 !important;
            }}
            
            .brand-gradient {{
                background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 600;
            }}
            
            button, .stButton>button {{
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
                color: white !important;
                transition: all 0.3s ease !important;
                border-radius: 0.75rem !important;
                box-shadow: 0 3px 8px rgba(45,135,211,0.3) !important;
                font-weight: 500 !important;
                letter-spacing: 0.3px !important;
                padding: 0.6rem 1.2rem !important;
                border: none !important;
            }}
            
            button:hover, .stButton>button:hover {{
                transform: translateY(-3px) !important;
                box-shadow: 0 6px 15px rgba(45,135,211,0.4) !important;
            }}
            
            .chat-message.user {{
                background-color: var(--accent-color);
                border-left: 5px solid var(--primary-color);
            }}
            
            .message-model {{
                background-color: rgba(45,135,211,0.08);
                border: 1px solid rgba(45,135,211,0.15);
                color: var(--primary-color);
            }}
            
            .footer {{
                margin-top: 2.5rem;
                padding: 1.5rem;
                text-align: center;
                background-color: var(--background-color);
                border-radius: 1rem;
                box-shadow: 0 -2px 10px rgba(0,0,0,0.03);
            }}
            
            /* Company logo styling */
            .company-logo {{
                max-height: 50px;
                margin-right: 1rem;
            }}
            
            {self.branding.custom_css}
        </style>
        """
        
        return base_css
    
    def get_header_html(self) -> str:
        """Generate branded header HTML"""
        logo_html = ""
        if self.branding.company_logo_url:
            logo_html = f'<img src="{self.branding.company_logo_url}" class="company-logo" alt="{self.branding.company_name}">'
        
        return f"""
        <header>
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                {logo_html}
                <div>
                    <h1 class="brand-title">{self.branding.app_title}</h1>
                    <p style="font-size: 1.2rem; color: #555; margin-top: -0.5rem; margin-bottom: 1.5rem; font-weight: 300; line-height: 1.6;">
                        {self.branding.app_description}
                        {f'<br><span class="brand-gradient">{self.branding.app_tagline}</span>' if self.branding.app_tagline else ''}
                    </p>
                </div>
            </div>
        </header>
        """
    
    def get_footer_html(self) -> str:
        """Generate branded footer HTML"""
        powered_by_html = ""
        if self.branding.show_powered_by:
            powered_by_html = f"""
            <div style="color: #666; margin-bottom: 1.5rem; font-size: 1.05rem;">
                Powered by <span class="brand-gradient">Model Context Protocol (MCP)</span>
            </div>
            """
        
        custom_footer = ""
        if self.branding.custom_footer_text:
            custom_footer = f"<div style='margin-bottom: 1rem;'>{self.branding.custom_footer_text}</div>"
        
        support_links = ""
        if self.branding.company_website or self.branding.company_support_email:
            links = []
            if self.branding.company_website:
                links.append(f'<a href="{self.branding.company_website}" style="color: var(--primary-color);">Website</a>')
            if self.branding.company_support_email:
                links.append(f'<a href="mailto:{self.branding.company_support_email}" style="color: var(--primary-color);">Support</a>')
            support_links = f"<div style='margin-bottom: 1rem;'>{' · '.join(links)}</div>"
        
        return f"""
        <div class="footer">
            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 1.2rem;">
                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-right: 0.8rem; box-shadow: 0 4px 10px rgba(45,135,211,0.3);">
                    <span style="font-size: 24px;">{self.branding.app_icon}</span>
                </div>
                <div style="font-weight: 700; font-size: 1.3rem; color: var(--primary-color); letter-spacing: -0.5px;">{self.branding.company_name}</div>
            </div>
            
            {powered_by_html}
            {custom_footer}
            {support_links}
            
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(0,0,0,0.05); color: #888; font-size: 0.9rem; font-weight: 400;">
                {self.branding.copyright_text}
            </div>
        </div>
        """

# Pre-defined white-label templates
def create_template_configs():
    """Create pre-defined templates for different use cases"""
    
    templates = {
        "corporate": {
            "branding": {
                "company_name": "Enterprise AI Solutions",
                "app_title": "AI Assistant Platform",
                "app_description": "Enterprise-grade AI assistance for your business",
                "app_tagline": "Powered by Advanced AI Technology",
                "primary_color": "#1a365d",
                "secondary_color": "#2c5282",
                "show_powered_by": False
            },
            "features": {
                "enable_conversation_starters": False,
                "enable_image_generation": True,
                "max_messages_per_session": 50
            }
        },
        
        "education": {
            "branding": {
                "company_name": "EduAI Assistant",
                "app_title": "Learning Companion",
                "app_description": "AI-powered educational assistance for students and teachers",
                "app_tagline": "Learning Made Smarter",
                "primary_color": "#38a169",
                "secondary_color": "#68d391",
                "app_icon": "🎓"
            },
            "features": {
                "enable_deep_thinking": True,
                "enable_model_comparison": True,
                "max_messages_per_session": 30
            }
        },
        
        "healthcare": {
            "branding": {
                "company_name": "MedAI Assistant",
                "app_title": "Healthcare AI Companion",
                "app_description": "AI assistance for healthcare professionals",
                "app_tagline": "Enhancing Patient Care with AI",
                "primary_color": "#e53e3e",
                "secondary_color": "#fc8181",
                "app_icon": "🏥"
            },
            "features": {
                "enable_file_upload": True,
                "enable_export_conversation": True,
                "max_messages_per_session": 100
            }
        },
        
        "creative": {
            "branding": {
                "company_name": "CreativeAI Studio",
                "app_title": "Creative AI Assistant",
                "app_description": "AI-powered creativity and content generation",
                "app_tagline": "Unleash Your Creative Potential",
                "primary_color": "#9f7aea",
                "secondary_color": "#c5a3ff",
                "app_icon": "🎨"
            },
            "features": {
                "enable_image_generation": True,
                "enable_conversation_starters": True,
                "enable_model_comparison": True
            }
        }
    }
    
    return templates

# Configuration management functions
def setup_white_label_deployment(template_name: str = None, custom_config: Dict = None):
    """Set up a white-label deployment with optional template"""
    
    config = WhiteLabelConfig()
    
    if template_name:
        templates = create_template_configs()
        if template_name in templates:
            template = templates[template_name]
            
            # Apply template branding
            for key, value in template.get('branding', {}).items():
                if hasattr(config.branding, key):
                    setattr(config.branding, key, value)
            
            # Apply template features
            for key, value in template.get('features', {}).items():
                if hasattr(config.features, key):
                    setattr(config.features, key, value)
    
    # Apply custom configuration if provided
    if custom_config:
        for section, settings in custom_config.items():
            if hasattr(config, section):
                section_obj = getattr(config, section)
                for key, value in settings.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
    
    # Save configuration
    config.save_config()
    return config

def generate_deployment_package(config: WhiteLabelConfig, output_dir: str = "white_label_deployment"):
    """Generate a complete deployment package for white-label distribution"""
    
    import shutil
    import os
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Copy all necessary files
    files_to_copy = [
        'app.py', 'model_handler.py', 'model_recommender.py', 'mcp_handler.py',
        'conversation_starters.py', 'image_generator.py', 'utils.py', 'config.py',
        'white_label_config.py', 'pyproject.toml', '.replit'
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, output_dir)
    
    # Generate customized configuration file
    config_path = os.path.join(output_dir, 'white_label_config.json')
    with open(config_path, 'w') as f:
        json.dump({
            'branding': asdict(config.branding),
            'features': asdict(config.features),
            'deployment': asdict(config.deployment)
        }, f, indent=2)
    
    # Generate deployment instructions
    instructions = f"""
# White Label Deployment Instructions

## Configuration
Your white-label configuration has been set up in `white_label_config.json`.

## Deployment Steps
1. Upload all files to your Replit workspace
2. Set up required API keys in Replit Secrets:
   - OPENAI_API_KEY
   - ANTHROPIC_API_KEY
   - GEMINI_API_KEY (optional)
3. Run the application with the provided `.replit` configuration
4. Deploy using Replit's deployment feature

## Branding
- Company: {config.branding.company_name}
- App Title: {config.branding.app_title}
- Primary Color: {config.branding.primary_color}

## Features Enabled
- Model Comparison: {config.features.enable_model_comparison}
- Image Generation: {config.features.enable_image_generation}
- File Upload: {config.features.enable_file_upload}
- Deep Thinking: {config.features.enable_deep_thinking}

## Support
For technical support, contact your white-label provider.
"""
    
    with open(os.path.join(output_dir, 'DEPLOYMENT_INSTRUCTIONS.md'), 'w') as f:
        f.write(instructions)
    
    return output_dir

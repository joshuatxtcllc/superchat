
#!/usr/bin/env python3
"""
White Label Setup and Deployment Script
Creates customized deployments for different clients/use cases
"""

from white_label_config import WhiteLabelConfig, setup_white_label_deployment, generate_deployment_package, create_template_configs
import json
import sys

def interactive_setup():
    """Interactive setup for white-label configuration"""
    
    print("🎨 White Label Configuration Setup")
    print("=" * 50)
    
    # Choose template or custom
    print("\n📋 Available Templates:")
    templates = create_template_configs()
    template_list = list(templates.keys())
    
    for i, template in enumerate(template_list, 1):
        print(f"{i}. {template.title()}")
    print(f"{len(template_list) + 1}. Custom (start from scratch)")
    
    choice = input(f"\nSelect template (1-{len(template_list) + 1}): ").strip()
    
    template_name = None
    if choice.isdigit() and 1 <= int(choice) <= len(template_list):
        template_name = template_list[int(choice) - 1]
        print(f"✅ Selected template: {template_name.title()}")
    
    # Custom branding configuration
    print("\n🎨 Branding Configuration")
    print("-" * 30)
    
    company_name = input("Company Name: ").strip() or "AI Assistant Company"
    app_title = input("App Title: ").strip() or "AI Assistant Platform"
    app_description = input("App Description: ").strip() or "Advanced AI assistance platform"
    
    # Color scheme
    print("\n🎨 Color Scheme (hex colors):")
    primary_color = input("Primary Color (#2D87D3): ").strip() or "#2D87D3"
    secondary_color = input("Secondary Color (#36a9e1): ").strip() or "#36a9e1"
    
    # Features configuration
    print("\n⚙️ Features Configuration")
    print("-" * 30)
    
    def ask_yes_no(question, default=True):
        default_str = "Y/n" if default else "y/N"
        response = input(f"{question} ({default_str}): ").strip().lower()
        if not response:
            return default
        return response in ['y', 'yes', '1', 'true']
    
    enable_model_comparison = ask_yes_no("Enable Model Comparison?", True)
    enable_image_generation = ask_yes_no("Enable Image Generation?", True)
    enable_file_upload = ask_yes_no("Enable File Upload?", True)
    enable_deep_thinking = ask_yes_no("Enable Deep Thinking Mode?", True)
    
    # Custom configuration
    custom_config = {
        "branding": {
            "company_name": company_name,
            "app_title": app_title,
            "app_description": app_description,
            "primary_color": primary_color,
            "secondary_color": secondary_color
        },
        "features": {
            "enable_model_comparison": enable_model_comparison,
            "enable_image_generation": enable_image_generation,
            "enable_file_upload": enable_file_upload,
            "enable_deep_thinking": enable_deep_thinking
        }
    }
    
    # Create configuration
    config = setup_white_label_deployment(template_name, custom_config)
    
    print("\n✅ Configuration Created Successfully!")
    print(f"📁 Configuration saved to: white_label_config.json")
    
    # Ask if they want to generate deployment package
    if ask_yes_no("\n📦 Generate deployment package?", True):
        output_dir = f"white_label_deployment_{company_name.lower().replace(' ', '_')}"
        package_dir = generate_deployment_package(config, output_dir)
        print(f"📦 Deployment package created in: {package_dir}")
        print("\n🚀 Next Steps:")
        print("1. Upload the deployment package to your Replit workspace")
        print("2. Configure API keys in Replit Secrets")
        print("3. Run the application")
        print("4. Deploy using Replit's deployment feature")
    
    return config

def create_predefined_deployments():
    """Create predefined deployments for common use cases"""
    
    print("🏭 Creating Predefined White Label Deployments")
    print("=" * 60)
    
    templates = create_template_configs()
    
    for template_name, template_config in templates.items():
        print(f"\n📦 Creating {template_name.title()} deployment...")
        
        # Set up configuration
        config = setup_white_label_deployment(template_name)
        
        # Generate deployment package
        output_dir = f"white_label_{template_name}"
        package_dir = generate_deployment_package(config, output_dir)
        
        print(f"✅ {template_name.title()} deployment created in: {package_dir}")
    
    print("\n🎉 All predefined deployments created successfully!")
    print("\nAvailable deployments:")
    for template_name in templates.keys():
        print(f"- white_label_{template_name}/")

def main():
    """Main script entry point"""
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "interactive":
            interactive_setup()
        elif command == "predefined":
            create_predefined_deployments()
        elif command == "templates":
            print("📋 Available Templates:")
            templates = create_template_configs()
            for name, config in templates.items():
                print(f"\n{name.title()}:")
                print(f"  Company: {config['branding']['company_name']}")
                print(f"  App: {config['branding']['app_title']}")
                print(f"  Description: {config['branding']['app_description']}")
        else:
            print(f"Unknown command: {command}")
            print_usage()
    else:
        print_usage()

def print_usage():
    """Print script usage information"""
    print("""
🎨 White Label Setup Script

Usage:
  python white_label_setup.py <command>

Commands:
  interactive   - Interactive setup wizard
  predefined    - Create all predefined template deployments
  templates     - List available templates

Examples:
  python white_label_setup.py interactive
  python white_label_setup.py predefined
  python white_label_setup.py templates
""")

if __name__ == "__main__":
    main()
def create_template_configs():
    """Create template configurations for different use cases"""
    return {
        "corporate": {
            "branding": {
                "company_name": "Enterprise Solutions Inc.",
                "app_title": "Corporate AI Assistant",
                "app_description": "Professional AI assistance for enterprise workflows",
                "app_icon": "🏢",
                "app_tagline": "Empowering business with AI",
                "primary_color": "#1f4e79",
                "secondary_color": "#2d87d3",
                "company_logo_url": "",
                "company_website": "https://yourcompany.com",
                "company_support_email": "support@yourcompany.com",
                "custom_footer_text": "Enterprise AI Solutions",
                "copyright_text": "© 2024 Enterprise Solutions Inc.",
                "show_powered_by": False
            },
            "features": {
                "enable_model_comparison": True,
                "enable_deep_thinking": True,
                "enable_image_generation": False,
                "enable_file_upload": True,
                "enable_conversation_starters": True,
                "enable_model_recommender": True,
                "max_messages_per_session": 100,
                "default_model": "gpt-4o",
                "min_time_between_messages": 1.0
            }
        },
        "education": {
            "branding": {
                "company_name": "EduTech Learning",
                "app_title": "Educational AI Tutor",
                "app_description": "AI-powered learning assistant for students and educators",
                "app_icon": "🎓",
                "app_tagline": "Learn smarter with AI",
                "primary_color": "#2e8b57",
                "secondary_color": "#90ee90",
                "company_logo_url": "",
                "company_website": "https://edutech.com",
                "company_support_email": "help@edutech.com",
                "custom_footer_text": "Making learning accessible for everyone",
                "copyright_text": "© 2024 EduTech Learning",
                "show_powered_by": True
            },
            "features": {
                "enable_model_comparison": True,
                "enable_deep_thinking": True,
                "enable_image_generation": True,
                "enable_file_upload": True,
                "enable_conversation_starters": True,
                "enable_model_recommender": True,
                "max_messages_per_session": 50,
                "default_model": "gpt-4o-mini",
                "min_time_between_messages": 0.5
            }
        },
        "healthcare": {
            "branding": {
                "company_name": "HealthAI Solutions",
                "app_title": "Medical AI Assistant",
                "app_description": "AI support for healthcare professionals and research",
                "app_icon": "🏥",
                "app_tagline": "Advancing healthcare with AI",
                "primary_color": "#dc143c",
                "secondary_color": "#ff6b6b",
                "company_logo_url": "",
                "company_website": "https://healthai.com",
                "company_support_email": "support@healthai.com",
                "custom_footer_text": "Not for diagnostic purposes",
                "copyright_text": "© 2024 HealthAI Solutions",
                "show_powered_by": False
            },
            "features": {
                "enable_model_comparison": False,
                "enable_deep_thinking": True,
                "enable_image_generation": False,
                "enable_file_upload": True,
                "enable_conversation_starters": False,
                "enable_model_recommender": False,
                "max_messages_per_session": 30,
                "default_model": "claude-3-5-sonnet-20241022",
                "min_time_between_messages": 2.0
            }
        },
        "creative": {
            "branding": {
                "company_name": "Creative Studio AI",
                "app_title": "Creative AI Companion",
                "app_description": "AI-powered creativity and content generation platform",
                "app_icon": "🎨",
                "app_tagline": "Unleash your creativity",
                "primary_color": "#9932cc",
                "secondary_color": "#da70d6",
                "company_logo_url": "",
                "company_website": "https://creativestudio.ai",
                "company_support_email": "hello@creativestudio.ai",
                "custom_footer_text": "Where imagination meets AI",
                "copyright_text": "© 2024 Creative Studio AI",
                "show_powered_by": True
            },
            "features": {
                "enable_model_comparison": True,
                "enable_deep_thinking": False,
                "enable_image_generation": True,
                "enable_file_upload": True,
                "enable_conversation_starters": True,
                "enable_model_recommender": True,
                "max_messages_per_session": 200,
                "default_model": "gpt-4o",
                "min_time_between_messages": 0.0
            }
        }
    }

def setup_white_label_deployment(config):
    """Set up a white label deployment with the given configuration"""
    try:
        # Save the configuration
        config.save_config()
        
        # Create any necessary directories
        os.makedirs("conversation_history", exist_ok=True)
        os.makedirs("attached_assets", exist_ok=True)
        
        return {
            "success": True,
            "message": "White label deployment configured successfully",
            "config_file": "white_label_config.json"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to setup deployment: {str(e)}"
        }

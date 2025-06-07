
import streamlit as st
import json
import os
import time
from datetime import datetime
from white_label_config import WhiteLabelConfig, setup_white_label_deployment, create_template_configs
from hub_connection_manager import HubConnectionManager

class ConfigurationManager:
    """Streamlit interface for managing white label configuration"""
    
    def __init__(self):
        self.config = WhiteLabelConfig()
        self.hub_manager = HubConnectionManager(self.config)
    
    def render_configuration_interface(self):
        """Render the complete configuration interface"""
        
        st.title("🔧 White Label Configuration Manager")
        
        # Configuration tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎨 Branding", 
            "⚙️ Features", 
            "🌐 Deployment", 
            "🔗 Hub Connection",
            "📋 Templates"
        ])
        
        with tab1:
            self._render_branding_config()
        
        with tab2:
            self._render_features_config()
        
        with tab3:
            self._render_deployment_config()
        
        with tab4:
            self._render_connection_config()
        
        with tab5:
            self._render_template_config()
        
        # Save configuration
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save Configuration", type="primary"):
                if self.config.save_config():
                    st.success("Configuration saved successfully!")
                else:
                    st.error("Failed to save configuration")
        
        with col2:
            if st.button("🔄 Reset to Defaults"):
                self.config = WhiteLabelConfig()
                st.rerun()
        
        with col3:
            if st.button("🧪 Test Hub Connection"):
                self._test_hub_connection()
    
    def _render_branding_config(self):
        """Render branding configuration"""
        st.header("Brand Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Company Information")
            self.config.branding.company_name = st.text_input(
                "Company Name", 
                value=self.config.branding.company_name
            )
            
            self.config.branding.company_website = st.text_input(
                "Company Website", 
                value=self.config.branding.company_website
            )
            
            self.config.branding.company_support_email = st.text_input(
                "Support Email", 
                value=self.config.branding.company_support_email
            )
            
            self.config.branding.company_logo_url = st.text_input(
                "Company Logo URL", 
                value=self.config.branding.company_logo_url,
                help="Enter the URL of your company logo image (e.g., https://example.com/logo.png)"
            )
            
            st.subheader("App Information")
            self.config.branding.app_title = st.text_input(
                "App Title", 
                value=self.config.branding.app_title
            )
            
            self.config.branding.app_description = st.text_area(
                "App Description", 
                value=self.config.branding.app_description
            )
            
            self.config.branding.app_icon = st.text_input(
                "App Icon (emoji)", 
                value=self.config.branding.app_icon
            )
            
            self.config.branding.app_tagline = st.text_input(
                "App Tagline", 
                value=self.config.branding.app_tagline
            )
        
        with col2:
            st.subheader("Colors & Styling")
            self.config.branding.primary_color = st.color_picker(
                "Primary Color", 
                value=self.config.branding.primary_color
            )
            
            self.config.branding.secondary_color = st.color_picker(
                "Secondary Color", 
                value=self.config.branding.secondary_color
            )
            
            self.config.branding.background_color = st.color_picker(
                "Background Color", 
                value=self.config.branding.background_color
            )
            
            self.config.branding.accent_color = st.color_picker(
                "Accent Color", 
                value=self.config.branding.accent_color
            )
            
            self.config.branding.text_color = st.color_picker(
                "Text Color", 
                value=self.config.branding.text_color
            )
            
            st.subheader("Footer Settings")
            self.config.branding.show_powered_by = st.checkbox(
                "Show 'Powered by MCP'", 
                value=self.config.branding.show_powered_by
            )
            
            self.config.branding.custom_footer_text = st.text_area(
                "Custom Footer Text", 
                value=self.config.branding.custom_footer_text
            )
            
            self.config.branding.copyright_text = st.text_input(
                "Copyright Text", 
                value=self.config.branding.copyright_text
            )
            
            self.config.branding.custom_css = st.text_area(
                "Custom CSS", 
                value=self.config.branding.custom_css,
                help="Add custom CSS to override default styling"
            )
        
        # Preview
        st.subheader("Preview")
        st.markdown(self.config.get_header_html(), unsafe_allow_html=True)
    
    def _render_features_config(self):
        """Render features configuration"""
        st.header("Feature Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Core Features")
            self.config.features.enable_model_comparison = st.checkbox(
                "Model Comparison", 
                value=self.config.features.enable_model_comparison
            )
            
            self.config.features.enable_deep_thinking = st.checkbox(
                "Deep Thinking Mode", 
                value=self.config.features.enable_deep_thinking
            )
            
            self.config.features.enable_image_generation = st.checkbox(
                "Image Generation", 
                value=self.config.features.enable_image_generation
            )
            
            self.config.features.enable_file_upload = st.checkbox(
                "File Upload", 
                value=self.config.features.enable_file_upload
            )
        
        with col2:
            st.subheader("Limits & Settings")
            self.config.features.max_messages_per_session = st.number_input(
                "Max Messages per Session", 
                min_value=1, 
                max_value=1000,
                value=self.config.features.max_messages_per_session
            )
            
            self.config.features.default_model = st.selectbox(
                "Default Model", 
                options=["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
                index=0 if self.config.features.default_model == "gpt-4o" else 1
            )
            
            self.config.features.min_time_between_messages = st.slider(
                "Min Time Between Messages (seconds)", 
                min_value=0.0, 
                max_value=10.0,
                value=self.config.features.min_time_between_messages,
                step=0.5
            )
    
    def _render_deployment_config(self):
        """Render deployment configuration"""
        st.header("Deployment Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self.config.deployment.server_host = st.text_input(
                "Server Host", 
                value=self.config.deployment.server_host
            )
            
            self.config.deployment.server_port = st.number_input(
                "Server Port", 
                min_value=1000, 
                max_value=65535,
                value=self.config.deployment.server_port
            )
            
            self.config.deployment.debug_mode = st.checkbox(
                "Debug Mode", 
                value=self.config.deployment.debug_mode
            )
        
        with col2:
            self.config.deployment.daily_message_limit = st.number_input(
                "Daily Message Limit", 
                min_value=1,
                value=self.config.deployment.daily_message_limit
            )
            
            self.config.deployment.enable_analytics = st.checkbox(
                "Enable Analytics", 
                value=self.config.deployment.enable_analytics
            )
            
            if self.config.deployment.enable_analytics:
                self.config.deployment.analytics_tracking_id = st.text_input(
                    "Analytics Tracking ID", 
                    value=self.config.deployment.analytics_tracking_id
                )
    
    def _render_connection_config(self):
        """Render Hub connection configuration"""
        st.header("Hub Dashboard Connection")
        
        # Connection toggle
        self.config.connection.enable_hub_integration = st.checkbox(
            "Enable Hub Integration", 
            value=self.config.connection.enable_hub_integration,
            help="Connect to your Central Hub Dashboard for analytics and management"
        )
        
        if self.config.connection.enable_hub_integration:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Connection Details")
                self.config.connection.hub_dashboard_url = st.text_input(
                    "Hub Dashboard URL", 
                    value=self.config.connection.hub_dashboard_url,
                    placeholder="https://your-hub-dashboard.replit.dev"
                )
                
                self.config.connection.hub_api_key = st.text_input(
                    "Hub API Key", 
                    value=self.config.connection.hub_api_key,
                    type="password",
                    help="API key generated by your Hub Dashboard"
                )
                
                self.config.connection.app_id = st.text_input(
                    "App ID", 
                    value=self.config.connection.app_id,
                    help="Unique identifier for this app in the Hub"
                )
            
            with col2:
                st.subheader("Advanced Settings")
                self.config.connection.connection_timeout = st.number_input(
                    "Connection Timeout (seconds)", 
                    min_value=5, 
                    max_value=300,
                    value=self.config.connection.connection_timeout
                )
                
                self.config.connection.retry_attempts = st.number_input(
                    "Retry Attempts", 
                    min_value=1, 
                    max_value=10,
                    value=self.config.connection.retry_attempts
                )
                
                self.config.connection.enable_real_time_sync = st.checkbox(
                    "Enable Real-time Sync", 
                    value=self.config.connection.enable_real_time_sync,
                    help="Use WebSocket for real-time updates"
                )
            
            # Connection status
            st.subheader("Connection Status")
            
            if st.button("Test Connection Now"):
                with st.spinner("Testing connection..."):
                    result = self.hub_manager.test_connection()
                    
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        if 'response_time' in result:
                            st.info(f"Response time: {result['response_time']:.2f}s")
                    else:
                        st.error(f"❌ {result['message']}")
            
            # Setup instructions
            with st.expander("📋 Setup Instructions"):
                st.markdown("""
                ### Quick Setup Steps:
                
                1. **Generate API Key** from your Hub Dashboard
                2. **Copy the generated API key** and paste it above
                3. **Set your App ID** (recommended: `multi-model-chat`)
                4. **Test the connection** using the button above
                
                ### Required Headers:
                Your Hub Dashboard expects these headers:
                - X-API-Key: your-generated-api-key
                - Content-Type: application/json
                
                ### Available Endpoints:
                - **Main API**: Your Hub Dashboard URL
                - **Events**: /api/events/publish
                - **Connection Test**: /api/test-connection
                """)
    
    def _render_template_config(self):
        """Render template configuration"""
        st.header("Configuration Templates")
        
        templates = create_template_configs()
        
        st.write("Choose a pre-configured template to quickly set up your white label deployment:")
        
        template_cols = st.columns(2)
        
        for i, (template_name, template_config) in enumerate(templates.items()):
            with template_cols[i % 2]:
                with st.container():
                    st.subheader(f"{template_config['branding']['app_icon']} {template_name.title()}")
                    st.write(template_config['branding']['app_description'])
                    
                    if st.button(f"Apply {template_name.title()} Template", key=f"template_{template_name}"):
                        # Apply template
                        for section, settings in template_config.items():
                            if hasattr(self.config, section):
                                section_obj = getattr(self.config, section)
                                for key, value in settings.items():
                                    if hasattr(section_obj, key):
                                        setattr(section_obj, key, value)
                        
                        st.success(f"{template_name.title()} template applied!")
                        st.rerun()
        
        # Export/Import configuration
        st.markdown("---")
        st.subheader("Import/Export Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📤 Export Configuration"):
                config_json = json.dumps({
                    'branding': self.config.branding.__dict__,
                    'features': self.config.features.__dict__,
                    'deployment': self.config.deployment.__dict__,
                    'connection': self.config.connection.__dict__
                }, indent=2)
                
                st.download_button(
                    label="Download Configuration JSON",
                    data=config_json,
                    file_name="white_label_config.json",
                    mime="application/json"
                )
        
        with col2:
            uploaded_file = st.file_uploader(
                "📁 Import Configuration",
                type=['json'],
                help="Upload a previously exported configuration file"
            )
            
            if uploaded_file is not None:
                try:
                    config_data = json.load(uploaded_file)
                    
                    # Apply imported configuration
                    for section, settings in config_data.items():
                        if hasattr(self.config, section):
                            section_obj = getattr(self.config, section)
                            for key, value in settings.items():
                                if hasattr(section_obj, key):
                                    setattr(section_obj, key, value)
                    
                    st.success("Configuration imported successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Failed to import configuration: {e}")
    
    def _test_hub_connection(self):
        """Test Hub connection and display results"""
        with st.spinner("Testing Hub connection..."):
            self.hub_manager = HubConnectionManager(self.config)
            result = self.hub_manager.test_connection()
            
            if result['success']:
                st.success(f"✅ {result['message']}")
                
                # Try to register the app
                reg_result = self.hub_manager.register_app()
                if reg_result['success']:
                    st.success(f"📱 App registered with Hub: {reg_result.get('registration_id', 'Success')}")
                else:
                    st.warning(f"⚠️ App registration failed: {reg_result['message']}")
                    
            else:
                st.error(f"❌ Connection failed: {result['message']}")
                st.info("💡 Make sure your Hub Dashboard is running and the URL/API key are correct")

def render_configuration_manager():
    """Render the configuration manager in Streamlit"""
    config_manager = ConfigurationManager()
    config_manager.render_configuration_interface()

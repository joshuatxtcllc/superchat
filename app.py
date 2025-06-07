import streamlit as st
import os
import json
from datetime import datetime
import time

from model_handler import ModelHandler
from model_recommender import ModelRecommender
from mcp_handler import MCPHandler
from conversation_starters import get_conversation_starters
from image_generator import ImageGenerator
from white_label_config import WhiteLabelConfig
from utils import (
    get_avatar, 
    format_message, 
    load_session_history, 
    save_session_history
)

# Initialize white-label configuration
wl_config = WhiteLabelConfig()

# Page configuration
st.set_page_config(
    page_title=wl_config.branding.app_title,
    page_icon=wl_config.branding.app_icon,
    layout="wide"
)

# Apply custom branded CSS
st.markdown(wl_config.get_custom_css(), unsafe_allow_html=True)

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_model' not in st.session_state:
    st.session_state.current_model = "gpt-4o"
if 'conversation_id' not in st.session_state:
    # Generate a unique conversation ID
    st.session_state.conversation_id = f"conv_{int(time.time())}"
if 'comparison_mode' not in st.session_state:
    st.session_state.comparison_mode = False
if 'comparison_models' not in st.session_state:
    st.session_state.comparison_models = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0
if 'last_message_time' not in st.session_state:
    st.session_state.last_message_time = 0

# Initialize handlers
model_handler = ModelHandler()
model_recommender = ModelRecommender()
mcp_handler = MCPHandler()
image_generator = ImageGenerator()

# Load saved messages if they exist
if st.session_state.conversation_id:
    saved_messages = load_session_history(st.session_state.conversation_id)
    if saved_messages and len(st.session_state.messages) == 0:
        st.session_state.messages = saved_messages

# Sidebar for settings
with st.sidebar:
    st.title("Chat Settings")

    # API Status
    with st.expander("API Status", expanded=False):
        openai_configured = bool(os.environ.get('OPENAI_API_KEY'))
        anthropic_configured = bool(os.environ.get('ANTHROPIC_API_KEY'))
        gemini_configured = bool(os.environ.get('GEMINI_API_KEY'))

        st.markdown("**OpenAI API:**")
        if openai_configured:
            st.success("✅ Configured")
        else:
            st.error("❌ Not configured - Add OPENAI_API_KEY to Secrets")

        st.markdown("**Anthropic API:**")
        if anthropic_configured:
            st.success("✅ Configured")
        else:
            st.error("❌ Not configured - Add ANTHROPIC_API_KEY to Secrets")

        st.markdown("**Gemini API:**")
        if gemini_configured:
            st.success("✅ Configured")
        else:
            st.error("❌ Not configured - Add GEMINI_API_KEY to Secrets")

        if not openai_configured and not anthropic_configured and not gemini_configured:
            st.warning("⚠️ No API keys configured. Please add them in the Secrets tool.")

    # Single model mode
    st.subheader("Model Selection")

    # Filter models based on white-label configuration
    available_models = list(model_handler.models.keys())
    if wl_config.features.allowed_models:
        available_models = [m for m in available_models if m in wl_config.features.allowed_models]

    # Model selector
    model_name = st.selectbox(
        "Select AI Model",
        options=available_models,
        index=available_models.index(
            next((k for k, v in model_handler.models.items() if v == st.session_state.current_model), available_models[0])
        ) if available_models else 0
    )

    # Show model information
    with st.expander("Model Information", expanded=False):
        model_info = model_handler.get_model_info(model_handler.models[model_name])
        st.markdown(f"**{model_name}**")
        st.markdown(f"*{model_info['description']}*")
        st.markdown("**Strengths:**")
        for strength in model_info['strengths']:
            st.markdown(f"- {strength}")
        st.markdown("**Suitable for:**")
        for use_case in model_info['use_cases']:
            st.markdown(f"- {use_case}")

    st.session_state.current_model = model_handler.models[model_name]

    # Toggle comparison mode (if enabled in white-label config)
    if wl_config.features.enable_model_comparison:
        st.divider()
        st.subheader("Comparison Mode")
        comparison_mode = st.toggle("Enable Model Comparison", value=st.session_state.comparison_mode)
        st.session_state.comparison_mode = comparison_mode

    # Deep thinking mode (if enabled in white-label config)
    if wl_config.features.enable_deep_thinking:
        st.divider()
        st.subheader("Deep Thinking")
        if 'deep_thinking' not in st.session_state:
            st.session_state.deep_thinking = False

        deep_thinking = st.toggle("Enable Deep Thinking", value=st.session_state.deep_thinking, 
                                 help="Shows the AI's reasoning process transparently")
        st.session_state.deep_thinking = deep_thinking

    if st.session_state.comparison_mode:
        st.session_state.comparison_models = st.multiselect(
            "Select models to compare",
            options=list(model_handler.models.keys()),
            default=[model_name] if st.session_state.comparison_models == [] else st.session_state.comparison_models
        )

    # Conversation management
    st.divider()
    st.subheader("Conversation")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.conversation_id = f"conv_{int(time.time())}"
        st.rerun()

    if st.button("Export Conversation"):
        conversation_data = {
            "conversation_id": st.session_state.conversation_id,
            "messages": st.session_state.messages,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.download_button(
            label="Download JSON",
            data=json.dumps(conversation_data, indent=2),
            file_name=f"conversation_{st.session_state.conversation_id}.json",
            mime="application/json"
        )

    st.divider()
    st.markdown("### Model Recommender")
    st.markdown("""
    Not sure which model to use? Our AI-powered recommender will analyze your task 
    and recommend the best model for you.
    """)
    if st.button("Ask for Recommendation"):
        st.session_state.show_recommender = True
        st.rerun()

    st.divider()
    st.markdown("### ⚙️ Configuration")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎨 Quick Settings", use_container_width=True):
            st.session_state.show_config = True
            st.rerun()

    with col2:
        if st.button("🔧 Configuration Manager", use_container_width=True):
            st.session_state.show_config_manager = True
            st.rerun()

    st.divider()
    st.markdown("### About MCP")
    st.markdown("""
    This interface implements the Model Context Protocol (MCP), which allows for 
    standardized interactions with different AI models. MCP enables models to:

    - Self-describe their capabilities
    - Receive and interpret specific instructions
    - Share context between models for seamless transitions
    - Optimize the conversation flow based on model strengths
    """)

# Configuration Manager interface
if 'show_config_manager' in st.session_state and st.session_state.show_config_manager:
    # Back button
    if st.button("← Back to Chat"):
        st.session_state.show_config_manager = False
        st.rerun()

    st.divider()

    # Import and render configuration manager
    try:
        from configuration_manager import render_configuration_manager
        render_configuration_manager()
    except Exception as e:
        st.error(f"Error loading Configuration Manager: {e}")
        st.info("Falling back to quick settings...")
        st.session_state.show_config_manager = False
        st.session_state.show_config = True
        st.rerun()

    st.stop()

# Main interface with branded header
st.markdown(wl_config.get_header_html(), unsafe_allow_html=True)

# Feature badges - hide behind a toggle button
if 'show_feature_badges' not in st.session_state:
    st.session_state.show_feature_badges = False

col_title, col_features = st.columns([4, 1])
with col_features:
    if st.button("ℹ️ Features", help="Show available features"):
        st.session_state.show_feature_badges = not st.session_state.show_feature_badges

if st.session_state.show_feature_badges:
    feature_badges = []
    if wl_config.features.enable_model_recommender:
        feature_badges.append("🤖 AI-powered recommender")

    if wl_config.features.enable_model_comparison:
        feature_badges.append("⚖️ Multi-model comparison")

    if feature_badges:
        st.info(" • ".join(feature_badges))

# Configuration interface
if 'show_config' in st.session_state and st.session_state.show_config:
    st.markdown("## ⚙️ Branding & Configuration Settings")

    # Add custom CSS for form styling
    st.markdown("""
    <style>
    .config-section {
        border: 1px solid #e0e0e0;
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background-color: rgba(255,255,255,0.8);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .config-header {
        color: #2D87D3;
        font-weight: 600;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.form("config_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="config-section">', unsafe_allow_html=True)
            st.markdown('<h3 class="config-header">Company Information</h3>', unsafe_allow_html=True)
            company_name = st.text_input("Company Name", value=wl_config.branding.company_name)
            company_website = st.text_input("Company Website", value=wl_config.branding.company_website)
            company_email = st.text_input("Support Email", value=wl_config.branding.company_support_email)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="config-section">', unsafe_allow_html=True)
            st.markdown('<h3 class="config-header">App Branding</h3>', unsafe_allow_html=True)
            app_title = st.text_input("App Title", value=wl_config.branding.app_title)
            app_description = st.text_area("App Description", value=wl_config.branding.app_description)
            app_icon = st.text_input("App Icon (emoji)", value=wl_config.branding.app_icon)
            app_tagline = st.text_input("App Tagline", value=wl_config.branding.app_tagline)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="config-section">', unsafe_allow_html=True)
            st.markdown('<h3 class="config-header">Colors & Styling</h3>', unsafe_allow_html=True)
            primary_color = st.color_picker("Primary Color", value=wl_config.branding.primary_color)
            secondary_color = st.color_picker("Secondary Color", value=wl_config.branding.secondary_color)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="config-section">', unsafe_allow_html=True)
            st.markdown('<h3 class="config-header">Footer Settings</h3>', unsafe_allow_html=True)
            show_powered_by = st.checkbox("Show 'Powered by MCP'", value=wl_config.branding.show_powered_by)
            custom_footer = st.text_area("Custom Footer Text", value=wl_config.branding.custom_footer_text)
            copyright_text = st.text_input("Copyright Text", value=wl_config.branding.copyright_text)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="config-section">', unsafe_allow_html=True)
            st.markdown('<h3 class="config-header">Features</h3>', unsafe_allow_html=True)
            enable_image_gen = st.checkbox("Enable Image Generation", value=wl_config.features.enable_image_generation)
            enable_file_upload = st.checkbox("Enable File Upload", value=wl_config.features.enable_file_upload)
            enable_model_comparison = st.checkbox("Enable Model Comparison", value=wl_config.features.enable_model_comparison)
            st.markdown('</div>', unsafe_allow_html=True)

        col_save, col_cancel = st.columns(2)

        with col_save:
            save_config = st.form_submit_button("💾 Save Configuration", type="primary", use_container_width=True)

        with col_cancel:
            cancel_config = st.form_submit_button("❌ Cancel", use_container_width=True)

        if save_config:
            # Update configuration
            wl_config.branding.company_name = company_name
            wl_config.branding.company_website = company_website
            wl_config.branding.company_support_email = company_email
            wl_config.branding.app_title = app_title
            wl_config.branding.app_description = app_description
            wl_config.branding.app_icon = app_icon
            wl_config.branding.app_tagline = app_tagline
            wl_config.branding.primary_color = primary_color
            wl_config.branding.secondary_color = secondary_color
            wl_config.branding.show_powered_by = show_powered_by
            wl_config.branding.custom_footer_text = custom_footer
            wl_config.branding.copyright_text = copyright_text
            wl_config.features.enable_image_generation = enable_image_gen
            wl_config.features.enable_file_upload = enable_file_upload
            wl_config.features.enable_model_comparison = enable_model_comparison

            # Save to file
            if wl_config.save_config():
                st.success("✅ Configuration saved successfully! Refreshing page...")
                st.session_state.show_config = False
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Failed to save configuration")

        if cancel_config:
            st.session_state.show_config = False
            st.rerun()

    st.divider()

# Model recommender section
if 'show_recommender' in st.session_state and st.session_state.show_recommender:
    st.markdown("### Model Recommender")
    st.markdown("Describe your task, and I'll recommend the best model for you.")
    task_description = st.text_area("Task Description", height=100, key="task_description")

    if st.button("Get Recommendation") and task_description.strip():
        with st.spinner("Analyzing your task..."):
            recommendation = model_recommender.get_recommendation(task_description)

        st.markdown(f"### Recommended Model: **{recommendation['model_name']}**")
        st.markdown(recommendation['explanation'])

        if st.button("Use Recommended Model"):
            st.session_state.current_model = model_handler.models[recommendation['model_name']]
            st.session_state.show_recommender = False
            st.rerun()

    if st.button("Cancel"):
        st.session_state.show_recommender = False
        st.rerun()

    st.divider()

# Conversation starters - collapsible interface (if enabled)
if len(st.session_state.messages) == 0 and wl_config.features.enable_conversation_starters:
    with st.expander("💬 Conversation Starters - Click to explore topics", expanded=False):
        # Use custom conversation starters if configured, otherwise use defaults
        if wl_config.features.custom_conversation_starters:
            starters = wl_config.features.custom_conversation_starters
        else:
            starters = get_conversation_starters()

        # Create tabs for different categories
        tab_names = list(starters.keys())
        tabs = st.tabs(tab_names)

        for i, (starter_category, starter_list) in enumerate(starters.items()):
            with tabs[i]:
                st.markdown(f"<h4 style='color: #2D87D3; margin-bottom: 16px;'>{starter_category}</h4>", unsafe_allow_html=True)

                # Display starters in a more compact format
                for starter in starter_list:
                    if st.button(starter, key=f"starter_{starter_category}_{starter}", use_container_width=True):
                        # Store the selected starter in session state
                        st.session_state.selected_starter = starter
                        st.rerun()

    st.divider()

# Process selected starter if exists
if 'selected_starter' in st.session_state and st.session_state.selected_starter:
    starter = st.session_state.selected_starter
    timestamp = datetime.now().strftime("%I:%M %p, %B %d")

    # Add user message to conversation
    st.session_state.messages.append({
        "role": "user", 
        "content": starter,
        "timestamp": timestamp
    })

    # Save conversation history
    save_session_history(st.session_state.conversation_id, st.session_state.messages)

    # Process with MCP if enabled
    messages_for_api = mcp_handler.prepare_messages(st.session_state.messages)

    # Get AI response using current model
    thinking_text = " (deep thinking enabled)" if st.session_state.deep_thinking else ""
    with st.spinner(f"Thinking{thinking_text}..."):
        response = model_handler.get_response(
            messages_for_api, 
            st.session_state.current_model,
            deep_thinking=st.session_state.deep_thinking
        )

        # Add MCP context if available
        mcp_context = mcp_handler.extract_mcp_context(response)

        # Add assistant message to conversation
        timestamp = datetime.now().strftime("%I:%M %p, %B %d")
        current_model_name = next((k for k, v in model_handler.models.items() if v == st.session_state.current_model), "AI")
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response,
            "timestamp": timestamp,
            "model": current_model_name,
            "model_id": st.session_state.current_model,
            "mcp_context": mcp_context,
            "deep_thinking": st.session_state.deep_thinking
        })

        # Save conversation history
        save_session_history(st.session_state.conversation_id, st.session_state.messages)

    # Clear the selected starter
    st.session_state.selected_starter = None

# Display chat messages with MCP information
for idx, message in enumerate(st.session_state.messages):
    with st.container():
        col1, col2 = st.columns([1, 12])

        with col1:
            avatar_html = get_avatar(message["role"])
            st.markdown(avatar_html, unsafe_allow_html=True)

        with col2:
            message_html = format_message(message)
            st.markdown(message_html, unsafe_allow_html=True)

            # Display MCP context information if available
            if message.get("mcp_context") and message["role"] == "assistant":
                with st.expander("MCP Context Information", expanded=False):
                    st.json(message["mcp_context"])

# Image generation section (if enabled) - hidden behind button
if wl_config.features.enable_image_generation:
    if 'show_image_generation' not in st.session_state:
        st.session_state.show_image_generation = False

    if st.button("🎨 AI Image Generation", help="Generate images with AI"):
        st.session_state.show_image_generation = not st.session_state.show_image_generation

    if st.session_state.show_image_generation:
        st.subheader("Generate Images with AI")

        col1, col2 = st.columns(2)

        with col1:
            image_prompt = st.text_area(
                "Image Description",
                height=100,
                placeholder="Describe the image you want to generate... Be as detailed as possible!",
                help="Example: A futuristic cityscape at sunset with flying cars and neon lights",
                key="image_prompt_input"
            )

            # AI Prompt Improver
            if st.button("🤖 Improve Prompt with AI", help="Let AI enhance your prompt for better results", use_container_width=True):
                if image_prompt.strip():
                    with st.spinner("Improving your prompt..."):
                        improvement_result = image_generator.improve_prompt(image_prompt)

                        if improvement_result.get("success"):
                            st.session_state.improved_prompt = improvement_result["improved_prompt"]
                            st.session_state.original_prompt = improvement_result["original_prompt"]
                            st.success("✨ Prompt improved!")
                            st.rerun()
                        else:
                            st.error(f"Error improving prompt: {improvement_result.get('error', 'Unknown error')}")
                else:
                    st.warning("Please enter a prompt first")

        # Show improved prompt if available (outside columns for better display)
        if 'improved_prompt' in st.session_state:
            st.markdown("---")
            st.subheader("🤖 AI-Improved Prompt")
            
            col_orig, col_improved = st.columns(2)
            with col_orig:
                st.markdown("**Original:**")
                st.text_area("Original prompt:", value=st.session_state.original_prompt, height=80, key="original_display", disabled=True)
            
            with col_improved:
                st.markdown("**Improved:**")
                improved_prompt_display = st.text_area("Improved prompt:", value=st.session_state.improved_prompt, height=80, key="improved_display")

            col_use, col_copy, col_clear = st.columns(3)
            with col_use:
                if st.button("✅ Use Improved Prompt", type="primary", use_container_width=True):
                    st.session_state.prompt_to_use = st.session_state.improved_prompt
                    st.success("Using improved prompt for generation!")

            with col_copy:
                if st.button("📋 Copy to Clipboard", use_container_width=True):
                    st.code(st.session_state.improved_prompt)
                    st.success("Improved prompt displayed above - select and copy!")

            with col_clear:
                if st.button("🗑️ Clear", use_container_width=True):
                    if 'improved_prompt' in st.session_state:
                        del st.session_state.improved_prompt
                    if 'original_prompt' in st.session_state:
                        del st.session_state.original_prompt
                    if 'prompt_to_use' in st.session_state:
                        del st.session_state.prompt_to_use
                    st.rerun()
            st.markdown("---")

        # Move back to the original column layout for generation settings
        col1, col2 = st.columns(2)
        with col1:

            image_model = st.selectbox(
                "Image Generation Model",
                options=list(image_generator.available_models.keys()),
                index=0
            )

            if image_model == "DALL-E 3":
                image_size = st.selectbox("Image Size", ["1024x1024", "1792x1024", "1024x1792"])
                image_quality = st.selectbox("Quality", ["standard", "hd"])
                image_style = st.selectbox("Style", ["vivid", "natural"])
            else:
                image_size = st.selectbox("Image Size", ["1024x1024", "512x512", "256x256"])
                image_quality = "standard"
                image_style = "vivid"

        with col2:
            if st.button("🎨 Generate Image", type="primary", use_container_width=True):
                # Use improved prompt if available and user clicked "Use Improved", otherwise use the original
                current_prompt = st.session_state.get('prompt_to_use', image_prompt)
                if current_prompt.strip():
                    with st.spinner("Generating image... This may take a moment..."):
                        result = image_generator.generate_image(
                            prompt=current_prompt,
                            model=image_generator.available_models[image_model],
                            size=image_size,
                            quality=image_quality,
                            style=image_style
                        )

                        if result.get("success"):
                            st.success("Image generated successfully!")
                            st.image(result["image_url"], caption=f"Generated: {current_prompt[:100]}...")

                            # Add generated image info to conversation
                            timestamp = datetime.now().strftime("%I:%M %p, %B %d")
                            prompt_info = f"Prompt: '{current_prompt}'"
                            if current_prompt != image_prompt:
                                prompt_info = f"Original prompt: '{image_prompt}'\nImproved prompt: '{current_prompt}'"

                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"I've generated an image based on your prompt.\n\n{prompt_info}\n\n[Image URL: {result['image_url']}]",
                                "timestamp": timestamp,
                                "model": f"Image Generator ({image_model})",
                                "model_id": result["model"],
                                "image_url": result["image_url"],
                                "image_prompt": current_prompt,
                                "original_prompt": image_prompt if current_prompt != image_prompt else None
                            })

                            # Save conversation history
                            save_session_history(st.session_state.conversation_id, st.session_state.messages)

                        else:
                            st.error(f"Error generating image: {result.get('error', 'Unknown error')}")
                else:
                    st.warning("Please enter a description for the image you want to generate.")

            st.markdown("""
            **Tips for better images:**
            - Be specific about style, colors, and mood
            - Include details about lighting and composition
            - Mention artistic styles if desired (e.g., "photorealistic", "watercolor", "digital art")
            - Specify the subject and setting clearly
            """)

# File upload and screen sharing section (if enabled)
if wl_config.features.enable_file_upload or wl_config.features.enable_screen_sharing:
    with st.expander("📎 File Upload & Screen Sharing", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📁 File Upload")
            uploaded_files = st.file_uploader(
                "Choose files to upload",
                accept_multiple_files=True,
                type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'pdf', 'txt', 'doc', 'docx', 'csv', 'json'],
                help="Upload images, documents, or text files to include in your conversation"
            )

            if uploaded_files:
                st.write(f"📁 {len(uploaded_files)} file(s) uploaded:")
                for file in uploaded_files:
                    st.write(f"- {file.name} ({file.type})")

        with col2:
            st.subheader("🖥️ Screen Sharing")
            st.markdown("**Share your screen with AI for analysis**")

            # Simplified screen capture button
            if st.button("🖥️ Capture Screen Instructions"):
                st.info("""
                To capture your screen:
                1. Take a screenshot using your system's screenshot tool
                2. Upload the screenshot using the file uploader above
                3. Ask the AI to analyze your screen content
                """)
                st.markdown("""
                **Screenshot shortcuts:**
                - **Windows**: Windows + Shift + S
                - **Mac**: Cmd + Shift + 4
                - **Linux**: PrtScn or Shift + PrtScn
                """)

            st.markdown("""
            **How to use Screen Sharing:**
            1. Click "Capture Screen" button
            2. Select the screen/window to share
            3. The screenshot will be automatically downloaded
            4. Upload the downloaded image using the file uploader above
            5. Ask AI to analyze your screen content
            """)

        if uploaded_files and st.button("Clear Files"):
            st.rerun()

# Copy conversation section (if enabled)
if len(st.session_state.messages) > 0 and (wl_config.features.enable_export_conversation or wl_config.features.enable_copy_conversation):
    with st.expander("📋 Export & Share Conversation", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            # Generate conversation text
            conversation_text = ""
            for msg in st.session_state.messages:
                role = "You" if msg["role"] == "user" else f"AI ({msg.get('model', 'Assistant')})"
                timestamp = msg.get("timestamp", "")
                conversation_text += f"{role} [{timestamp}]:\n{msg['content']}\n\n"

            if st.button("📋 Copy Conversation", use_container_width=True):
                st.text_area("Conversation text (select and copy):", conversation_text, height=200)
                st.success("Conversation text displayed above - select and copy manually")

        with col2:
            if st.button("📧 Prepare Email", use_container_width=True):
                email_subject = f"AI Conversation - {datetime.now().strftime('%Y-%m-%d')}"
                email_body = f"Subject: {email_subject}\n\n{conversation_text}"
                st.text_area("Email Content (copy this):", email_body, height=200)

        with col3:
            conversation_data = {
                "conversation_id": st.session_state.conversation_id,
                "messages": st.session_state.messages,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_messages": len(st.session_state.messages)
            }
            st.download_button(
                label="💾 Download JSON",
                data=json.dumps(conversation_data, indent=2),
                file_name=f"conversation_{st.session_state.conversation_id}.json",
                mime="application/json",
                use_container_width=True
            )

st.divider()

# Input area
with st.container():

    user_input = st.text_area("Your message", height=120, key="user_input", placeholder="Type your message here... Ask anything or select a conversation starter above!")

    col1, col2 = st.columns([5, 1])

    with col1:
        st.caption("💡 Type your message above and click 'Send' to get a response from the selected AI model")

    with col2:
        send_button = st.button("Send", use_container_width=True, type="primary")

    if send_button and user_input.strip():
        # Input validation
        if len(user_input) > 10000:
            st.error("Message too long. Please limit to 10,000 characters.")
            st.stop()

        # Basic rate limiting - max 20 messages per session
        if st.session_state.message_count >= 20:
            st.error("Message limit reached for this session. Please start a new conversation.")
            st.stop()

        # Time-based rate limiting - minimum 2 seconds between messages
        current_time = time.time()
        if current_time - st.session_state.last_message_time < 2:
            st.error("Please wait before sending another message.")
            st.stop()

        st.session_state.message_count += 1
        st.session_state.last_message_time = current_time
        # Add user message to conversation
        timestamp = datetime.now().strftime("%I:%M %p, %B %d")
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input,
            "timestamp": timestamp
        })

        # Save conversation history
        save_session_history(st.session_state.conversation_id, st.session_state.messages)

        # Process with MCP if enabled
        messages_for_api = mcp_handler.prepare_messages(st.session_state.messages)

        # Get uploaded files if any
        current_files = uploaded_files if 'uploaded_files' in locals() else None

        # In comparison mode, get responses from all selected models
        if st.session_state.comparison_mode and st.session_state.comparison_models:
            for model_name in st.session_state.comparison_models:
                model_id = model_handler.models[model_name]

                thinking_text = " (with deep thinking)" if st.session_state.deep_thinking else ""
                with st.spinner(f"Getting response from {model_name}{thinking_text}..."):
                    response = model_handler.get_response(
                        messages_for_api, 
                        model_id, 
                        deep_thinking=st.session_state.deep_thinking,
                        uploaded_files=current_files
                    )

                    # Add MCP context if available
                    mcp_context = mcp_handler.extract_mcp_context(response)

                    # Add assistant message to conversation
                    timestamp = datetime.now().strftime("%I:%M %p, %B %d")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "timestamp": timestamp,
                        "model": model_name,
                        "model_id": model_id,
                        "mcp_context": mcp_context,
                        "deep_thinking": st.session_state.deep_thinking,
                        "files_processed": len(current_files) if current_files else 0
                    })

                    # Save conversation history
                    save_session_history(st.session_state.conversation_id, st.session_state.messages)
        else:
            # Get AI response using current model
            thinking_text = " (deep thinking enabled)" if st.session_state.deep_thinking else ""
            with st.spinner(f"Thinking{thinking_text}..."):
                response = model_handler.get_response(
                    messages_for_api, 
                    st.session_state.current_model,
                    deep_thinking=st.session_state.deep_thinking,
                    uploaded_files=current_files
                )

                # Add MCP context if available
                mcp_context = mcp_handler.extract_mcp_context(response)

                # Add assistant message to conversation
                timestamp = datetime.now().strftime("%I:%M %p, %B %d")
                current_model_name = next((k for k, v in model_handler.models.items() if v == st.session_state.current_model), "AI")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response,
                    "timestamp": timestamp,
                    "model": current_model_name,
                    "model_id": st.session_state.current_model,
                    "mcp_context": mcp_context,
                    "deep_thinking": st.session_state.deep_thinking,
                    "files_processed": len(current_files) if current_files else 0
                })

                # Save conversation history
                save_session_history(st.session_state.conversation_id, st.session_state.messages)

        # Just rerun to update the UI
        # The text area will be cleared automatically on rerun
        st.rerun()

# Add branded footer - hidden behind toggle
if 'show_footer' not in st.session_state:
    st.session_state.show_footer = False

col_spacer, col_footer = st.columns([5, 1])
with col_footer:
    if st.button("ℹ️ About", help="Show app information"):
        st.session_state.show_footer = not st.session_state.show_footer

if st.session_state.show_footer:
    st.markdown(wl_config.get_footer_html(), unsafe_allow_html=True)
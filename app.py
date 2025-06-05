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
    st.markdown("### About MCP")
    st.markdown("""
    This interface implements the Model Context Protocol (MCP), which allows for 
    standardized interactions with different AI models. MCP enables models to:

    - Self-describe their capabilities
    - Receive and interpret specific instructions
    - Share context between models for seamless transitions
    - Optimize the conversation flow based on model strengths
    """)

# Main interface with branded header
st.markdown(wl_config.get_header_html(), unsafe_allow_html=True)

# Feature badges (conditional based on white-label config)
feature_badges = []
if wl_config.features.enable_model_recommender:
    feature_badges.append("""
        <div style="background-color: rgba(45,135,211,0.1); border-radius: 1rem; padding: 0.6rem 1.2rem; display: flex; align-items: center; font-size: 0.9rem; color: var(--primary-color); font-weight: 500;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 0.5rem;">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
            </svg>
            AI-powered recommender
        </div>
    """)

if wl_config.features.enable_model_comparison:
    feature_badges.append("""
        <div style="background-color: rgba(45,135,211,0.1); border-radius: 1rem; padding: 0.6rem 1.2rem; display: flex; align-items: center; font-size: 0.9rem; color: var(--primary-color); font-weight: 500;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 0.5rem;">
                <path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"></path>
                <path d="M9 12h6"></path>
                <path d="M12 9v6"></path>
            </svg>
            Multi-model comparison
        </div>
    """)

if feature_badges:
    st.markdown(f"""
    <div style="display: flex; gap: 1rem; margin-top: 1rem; flex-wrap: wrap;">
        {''.join(feature_badges)}
    </div>
    """, unsafe_allow_html=True)

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

# Image generation section (if enabled)
if wl_config.features.enable_image_generation:
    with st.expander("🎨 AI Image Generation", expanded=False):
        st.subheader("Generate Images with AI")

    col1, col2 = st.columns(2)

    with col1:
        image_prompt = st.text_area(
            "Image Description",
            height=100,
            placeholder="Describe the image you want to generate... Be as detailed as possible!",
            help="Example: A futuristic cityscape at sunset with flying cars and neon lights"
        )

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
            if image_prompt.strip():
                with st.spinner("Generating image... This may take a moment..."):
                    result = image_generator.generate_image(
                        prompt=image_prompt,
                        model=image_generator.available_models[image_model],
                        size=image_size,
                        quality=image_quality,
                        style=image_style
                    )

                    if result.get("success"):
                        st.success("Image generated successfully!")
                        st.image(result["image_url"], caption=f"Generated: {image_prompt[:100]}...")

                        # Add generated image info to conversation
                        timestamp = datetime.now().strftime("%I:%M %p, %B %d")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"I've generated an image based on your prompt: '{image_prompt}'\n\n[Image URL: {result['image_url']}]",
                            "timestamp": timestamp,
                            "model": f"Image Generator ({image_model})",
                            "model_id": result["model"],
                            "image_url": result["image_url"],
                            "image_prompt": image_prompt
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

        # Screen capture using JavaScript
        screen_capture_js = """
        <div id="screen-capture-container">
            <button id="capture-screen" style="
                background: linear-gradient(135deg, #2D87D3, #36a9e1);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
                margin: 8px 0;
                box-shadow: 0 4px 10px rgba(45,135,211,0.3);
                transition: all 0.3s ease;
            " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 15px rgba(45,135,211,0.4)'" 
               onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 4px 10px rgba(45,135,211,0.3)'">
                🖥️ Capture Screen
            </button>
            <canvas id="screen-canvas" style="display: none;"></canvas>
            <div id="capture-status" style="margin-top: 10px; font-size: 0.9rem; color: #666;"></div>
        </div>

        <script>
        document.getElementById('capture-screen').addEventListener('click', async function() {
            const statusDiv = document.getElementById('capture-status');
            const canvas = document.getElementById('screen-canvas');
            const ctx = canvas.getContext('2d');

            try {
                statusDiv.innerHTML = '📷 Requesting screen access...';

                // Request screen capture
                const stream = await navigator.mediaDevices.getDisplayMedia({
                    video: { mediaSource: 'screen' }
                });

                statusDiv.innerHTML = '🎥 Screen captured! Processing...';

                // Create video element to capture frame
                const video = document.createElement('video');
                video.srcObject = stream;
                video.play();

                video.addEventListener('loadedmetadata', function() {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;

                    // Capture frame
                    ctx.drawImage(video, 0, 0);

                    // Convert to blob and create download link
                    canvas.toBlob(function(blob) {
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'screen-capture-' + new Date().getTime() + '.png';
                        a.click();

                        statusDiv.innerHTML = '✅ Screen captured and downloaded! Upload the image above.';

                        // Stop screen sharing
                        stream.getTracks().forEach(track => track.stop());

                        URL.revokeObjectURL(url);
                    }, 'image/png');
                });

            } catch (err) {
                console.error('Error capturing screen:', err);
                statusDiv.innerHTML = '❌ Screen capture failed. Please try again or upload a screenshot manually.';
            }
        });
        </script>
        """

        st.components.v1.html(screen_capture_js, height=150)

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
                st.code(conversation_text, language="text")
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
    st.markdown("""
    <div style='background: linear-gradient(to bottom, #f8f9fa, #f0f7ff); 
              padding: 1.5rem; 
              border-radius: 1.2rem; 
              box-shadow: 0 5px 20px rgba(0,0,0,0.08); 
              border: 1px solid rgba(45,135,211,0.1);
              position: relative;
              overflow: hidden;'>
        <div style='position: absolute; top: 0; left: 0; width: 100%; height: 3px; background: linear-gradient(90deg, transparent, #2D87D3, transparent);'></div>
    """, unsafe_allow_html=True)

    user_input = st.text_area("Your message", height=120, key="user_input", placeholder="Type your message here... Ask anything or select a conversation starter above!")

    col1, col2 = st.columns([5, 1])

    with col1:
        st.markdown("""
        <div style='display: flex; align-items: center; margin-top: -0.5rem;'>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2D87D3" stroke-width="2" style="margin-right: 0.5rem;">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12" y2="8"></line>
            </svg>
            <span style="color: #555; font-size: 0.9rem; font-weight: 400;">
                Type your message above and click 'Send' to get a response from the selected AI model
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        send_button = st.button("Send", use_container_width=True, type="primary")

    st.markdown("</div>", unsafe_allow_html=True)

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

# Add branded footer
st.markdown(wl_config.get_footer_html(), unsafe_allow_html=True)
import streamlit as st
import os
import json
from datetime import datetime
import time

from model_handler import ModelHandler
from model_recommender import ModelRecommender
from mcp_handler import MCPHandler
from conversation_starters import get_conversation_starters
from utils import (
    get_avatar, 
    format_message, 
    load_session_history, 
    save_session_history,
    custom_css
)

# Page configuration
st.set_page_config(
    page_title="Multi-Model Chat Interface",
    page_icon="💬",
    layout="wide"
)

# Apply custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_model' not in st.session_state:
    st.session_state.current_model = "gpt-4o"
if 'conversation_id' not in st.session_state:
    # Generate a unique conversation ID
    st.session_state.conversation_id = f"conv_{int(time.time())}"
if 'api_keys' not in st.session_state:
    st.session_state.api_keys = {}
if 'comparison_mode' not in st.session_state:
    st.session_state.comparison_mode = False
if 'comparison_models' not in st.session_state:
    st.session_state.comparison_models = []

# Initialize handlers
model_handler = ModelHandler()
model_recommender = ModelRecommender()
mcp_handler = MCPHandler()

# Load saved messages if they exist
if st.session_state.conversation_id:
    saved_messages = load_session_history(st.session_state.conversation_id)
    if saved_messages and len(st.session_state.messages) == 0:
        st.session_state.messages = saved_messages

# Sidebar for settings
with st.sidebar:
    st.title("Chat Settings")
    
    # API key management
    with st.expander("API Keys", expanded=False):
        openai_key = st.text_input(
            "OpenAI API Key", 
            value=st.session_state.api_keys.get('openai', os.environ.get('OPENAI_API_KEY', '')),
            type="password",
            help="You can find your API key in your OpenAI account settings."
        )
        st.session_state.api_keys['openai'] = openai_key
        
        anthropic_key = st.text_input(
            "Anthropic API Key", 
            value=st.session_state.api_keys.get('anthropic', os.environ.get('ANTHROPIC_API_KEY', '')),
            type="password",
            help="Required for Claude models"
        )
        st.session_state.api_keys['anthropic'] = anthropic_key
        
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
    
    # Single model mode
    st.subheader("Model Selection")
    # Model selector
    model_name = st.selectbox(
        "Select AI Model",
        options=list(model_handler.models.keys()),
        index=list(model_handler.get_model_keys()).index(
            next((k for k, v in model_handler.models.items() if v == st.session_state.current_model), "GPT-4o")
        )
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
    
    # Toggle comparison mode
    st.divider()
    st.subheader("Comparison Mode")
    comparison_mode = st.toggle("Enable Model Comparison", value=st.session_state.comparison_mode)
    st.session_state.comparison_mode = comparison_mode
    
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

# Main interface
st.markdown("""
<header>
    <h1>Multi-Model Chat Interface</h1>
    <p style="font-size: 1.2rem; color: #555; margin-top: -0.5rem; margin-bottom: 1.5rem; font-weight: 300; line-height: 1.6;">
        Interact with multiple AI models in one unified experience with
        <span style="background: linear-gradient(90deg, #2D87D3, #36a9e1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 600;">Model Context Protocol</span>
        support
    </p>
    <div style="display: flex; gap: 1rem; margin-top: 1rem;">
        <div style="background-color: rgba(45,135,211,0.1); border-radius: 1rem; padding: 0.6rem 1.2rem; display: flex; align-items: center; font-size: 0.9rem; color: #2D87D3; font-weight: 500;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 0.5rem;">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
            </svg>
            AI-powered recommender
        </div>
        <div style="background-color: rgba(45,135,211,0.1); border-radius: 1rem; padding: 0.6rem 1.2rem; display: flex; align-items: center; font-size: 0.9rem; color: #2D87D3; font-weight: 500;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 0.5rem;">
                <path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"></path>
                <path d="M9 12h6"></path>
                <path d="M12 9v6"></path>
            </svg>
            Multi-model comparison
        </div>
    </div>
</header>
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

# Conversation starters
if len(st.session_state.messages) == 0:
    st.markdown("### 💬 Conversation Starters")
    starters = get_conversation_starters()
    
    # Create 3 columns
    cols = st.columns(3)
    
    # Display starters in columns with improved styling
    for i, (starter_category, starter_list) in enumerate(starters.items()):
        with cols[i % 3]:
            st.markdown(f"<h4 style='color: #2D87D3; margin-bottom: 12px;'>{starter_category}</h4>", unsafe_allow_html=True)
            for starter in starter_list:
                # Create a simplified hash for the starter to use in HTML id
                starter_id = "".join([c if c.isalnum() else "_" for c in starter[:10]])
                starter_html = f"""
                <div class="conversation-starter" id="starter_{starter_category}_{starter_id}" onclick="
                    document.querySelector('[data-testid*=\"stButton\"]').click()
                ">
                    {starter}
                </div>
                """
                st.markdown(starter_html, unsafe_allow_html=True)
                if st.button(starter, key=f"starter_{starter_category}_{starter}"):
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
    with st.spinner("Thinking..."):
        response = model_handler.get_response(messages_for_api, st.session_state.current_model)
        
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
            "mcp_context": mcp_context
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
        send_button = st.button("""<span style="font-weight: 600;">Send</span>""", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if send_button and user_input.strip():
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
        
        # In comparison mode, get responses from all selected models
        if st.session_state.comparison_mode and st.session_state.comparison_models:
            for model_name in st.session_state.comparison_models:
                model_id = model_handler.models[model_name]
                
                with st.spinner(f"Getting response from {model_name}..."):
                    response = model_handler.get_response(messages_for_api, model_id)
                    
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
                        "mcp_context": mcp_context
                    })
                    
                    # Save conversation history
                    save_session_history(st.session_state.conversation_id, st.session_state.messages)
        else:
            # Get AI response using current model
            with st.spinner("Thinking..."):
                response = model_handler.get_response(messages_for_api, st.session_state.current_model)
                
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
                    "mcp_context": mcp_context
                })
                
                # Save conversation history
                save_session_history(st.session_state.conversation_id, st.session_state.messages)
        
        # Just rerun to update the UI
        # The text area will be cleared automatically on rerun
        st.rerun()

# Add a modern footer
st.markdown("""
<div class="footer">
    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 1.2rem;">
        <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #2D87D3, #36a9e1); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-right: 0.8rem; box-shadow: 0 4px 10px rgba(45,135,211,0.3);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                <path d="M9 11h6"></path>
                <path d="M12 8v6"></path>
            </svg>
        </div>
        <div style="font-weight: 700; font-size: 1.3rem; color: #2D87D3; letter-spacing: -0.5px;">Multi-Model Chat Interface</div>
    </div>
    
    <div style="color: #666; margin-bottom: 1.5rem; font-size: 1.05rem;">
        Powered by <span style="background: linear-gradient(90deg, #2D87D3, #36a9e1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 600;">Model Context Protocol (MCP)</span>
    </div>
    
    <div style="display: flex; justify-content: center; gap: 2rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
        <div style="display: flex; align-items: center; font-size: 0.95rem; color: #555; background-color: rgba(255,255,255,0.6); padding: 0.7rem 1.2rem; border-radius: 1rem; box-shadow: 0 3px 10px rgba(0,0,0,0.05); border: 1px solid rgba(0,0,0,0.03);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2D87D3" stroke-width="2" style="margin-right: 0.7rem;">
                <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                <path d="M9 12l2 2 4-4"></path>
            </svg>
            <span style="font-weight: 500;">Multiple AI Models</span>
        </div>
        <div style="display: flex; align-items: center; font-size: 0.95rem; color: #555; background-color: rgba(255,255,255,0.6); padding: 0.7rem 1.2rem; border-radius: 1rem; box-shadow: 0 3px 10px rgba(0,0,0,0.05); border: 1px solid rgba(0,0,0,0.03);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2D87D3" stroke-width="2" style="margin-right: 0.7rem;">
                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                <path d="M2 17l10 5 10-5"></path>
                <path d="M2 12l10 5 10-5"></path>
            </svg>
            <span style="font-weight: 500;">Smart Recommendations</span>
        </div>
        <div style="display: flex; align-items: center; font-size: 0.95rem; color: #555; background-color: rgba(255,255,255,0.6); padding: 0.7rem 1.2rem; border-radius: 1rem; box-shadow: 0 3px 10px rgba(0,0,0,0.05); border: 1px solid rgba(0,0,0,0.03);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2D87D3" stroke-width="2" style="margin-right: 0.7rem;">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
            <span style="font-weight: 500;">MCP Support</span>
        </div>
    </div>
    
    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(0,0,0,0.05); color: #888; font-size: 0.9rem; font-weight: 400;">
        © 2025 · All Rights Reserved · <span style="color: #2D87D3;">Terms of Service</span> · <span style="color: #2D87D3;">Privacy Policy</span>
    </div>
</div>
""", unsafe_allow_html=True)

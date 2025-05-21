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
st.title("Multi-Model Chat Interface")

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
    st.markdown("### Conversation Starters")
    starters = get_conversation_starters()
    
    # Create 3 columns
    cols = st.columns(3)
    
    # Display starters in columns
    for i, (starter_category, starter_list) in enumerate(starters.items()):
        with cols[i % 3]:
            st.markdown(f"**{starter_category}**")
            for starter in starter_list:
                if st.button(starter, key=f"starter_{starter_category}_{starter}"):
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
                    
                    st.rerun()
    
    st.divider()

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
    user_input = st.text_area("Your message", height=100, key="user_input")
    col1, col2 = st.columns([5, 1])
    
    with col1:
        st.caption("Type your message above and click 'Send' to get a response from the selected AI model.")
    
    with col2:
        send_button = st.button("Send")
    
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
        
        # Clear input and rerun to update the UI
        st.session_state.user_input = ""
        st.rerun()

# Add a footer
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; color: #888;">
    Multi-Model Chat Interface with MCP Support © 2025
</div>
""", unsafe_allow_html=True)

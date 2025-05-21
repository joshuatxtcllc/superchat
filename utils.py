import os
import json
from datetime import datetime

# Custom CSS for styling the chat interface
custom_css = """
<style>
    .main {
        padding: 0 1rem;
        max-width: 65rem;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1.2rem;
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        background-color: #f9f9f9;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .chat-message:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    .chat-message.user {
        background-color: #f0f7ff;
        border-left: 5px solid #2D87D3;
    }
    .chat-message.assistant {
        background-color: #fafafa;
        border-left: 5px solid #9E9E9E;
    }
    .avatar {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        margin-right: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .user-avatar {
        background: linear-gradient(135deg, #2D87D3, #1a5fa0);
        color: white;
    }
    .assistant-avatar {
        background: linear-gradient(135deg, #9E9E9E, #707070);
        color: white;
    }
    .message-content {
        flex-grow: 1;
    }
    .message-header {
        margin-bottom: 0.85rem;
        padding-bottom: 0.7rem;
        border-bottom: 1px solid rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .message-model {
        font-size: 0.85rem;
        color: #555;
        font-weight: 500;
        font-style: italic;
        padding: 0.3rem 0.7rem;
        background-color: rgba(45,135,211,0.08);
        border-radius: 1rem;
        border: 1px solid rgba(45,135,211,0.15);
    }
    .message-timestamp {
        font-size: 0.8rem;
        color: #888;
        font-weight: 400;
    }
    .message-text {
        line-height: 1.8;
        font-size: 1.02rem;
        color: #333;
    }

    /* Button styling */
    button, .stButton>button {
        transition: all 0.3s ease !important;
        border-radius: 0.75rem !important;
        box-shadow: 0 3px 8px rgba(0,0,0,0.1) !important;
        font-weight: 500 !important;
        letter-spacing: 0.3px !important;
        padding: 0.6rem 1.2rem !important;
        border: none !important;
    }
    button:hover, .stButton>button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 15px rgba(0,0,0,0.15) !important;
        background-color: #2678bd !important;
    }

    /* Input field styling */
    .stTextArea textarea, .stTextInput input {
        border-radius: 0.75rem !important;
        border: 1px solid #e0e0e0 !important;
        padding: 1rem !important;
        transition: all 0.3s ease !important;
        font-size: 1.05rem !important;
        background-color: rgba(255,255,255,0.8) !important;
        box-shadow: 0 3px 10px rgba(0,0,0,0.03) !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #2D87D3 !important;
        box-shadow: 0 0 0 3px rgba(45,135,211,0.2) !important;
        background-color: #ffffff !important;
    }

    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #f8f9fa !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa !important;
        border-radius: 0.5rem !important;
    }

    /* Conversation starters */
    .conversation-starter {
        padding: 0.8rem 1rem;
        background-color: #f8f9fa;
        border-radius: 0.75rem;
        margin-bottom: 0.75rem;
        cursor: pointer;
        transition: all 0.2s ease;
        border: 1px solid #e0e0e0;
    }
    .conversation-starter:hover {
        background-color: #f0f7ff;
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-color: #2D87D3;
    }

    /* Additional styles for model cards */
    .model-card {
        border: 1px solid #e0e0e0;
        border-radius: 1rem;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        background-color: #ffffff;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .model-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    }
    .model-card h3 {
        margin-top: 0;
        color: #2D87D3;
        font-weight: 600;
        font-size: 1.2rem;
    }
    .model-card-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 0.8rem 0;
    }
    .model-badge {
        background: linear-gradient(135deg, #f0f7ff, #e1effe);
        color: #2D87D3;
        padding: 0.3rem 0.7rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* App header styling */
    header {
        margin-bottom: 2rem;
    }
    h1 {
        background: linear-gradient(90deg, #2D87D3, #36a9e1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }

    /* Loading spinner */
    .stSpinner > div {
        border-color: #2D87D3 transparent transparent !important;
    }

    /* Footer styling */
    .footer {
        margin-top: 2.5rem;
        padding: 1.5rem;
        text-align: center;
        background-color: #f8f9fa;
        border-radius: 1rem;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.03);
    }
</style>
"""

def get_avatar(role):
    """Returns HTML for avatar based on the message role"""
    if role == "user":
        return '<div class="avatar user-avatar">👤</div>'
    else:
        return '<div class="avatar assistant-avatar">🤖</div>'

def format_message(message):
    """Formats a message for display in the chat interface"""
    role_display = "You" if message["role"] == "user" else "Assistant"
    timestamp = message.get("timestamp", "")
    model = message.get("model", "")

    model_display = f'<div class="message-model">Model: {model}</div>' if model else ''

    return f"""
    <div class="chat-message {message['role']}">
        <div class="message-content">
            <div class="message-header">
                <strong>{role_display}</strong>
                {model_display}
                <div class="message-timestamp">{timestamp}</div>
            </div>
            <div class="message-text">{message['content']}</div>
        </div>
    </div>
    """

def get_history_dir():
    """Gets the directory for storing conversation history"""
    # Create a directory for conversation history if it doesn't exist
    history_dir = os.path.join(os.getcwd(), "conversation_history")
    os.makedirs(history_dir, exist_ok=True)
    return history_dir

def save_session_history(conversation_id, messages):
    """Saves the conversation history to a file"""
    history_dir = get_history_dir()
    history_path = os.path.join(history_dir, f"{conversation_id}.json")

    try:
        with open(history_path, 'w') as f:
            json.dump(messages, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving conversation history: {str(e)}")
        return False

def load_session_history(conversation_id):
    """Loads the conversation history from a file"""
    history_dir = get_history_dir()
    history_path = os.path.join(history_dir, f"{conversation_id}.json")

    try:
        if os.path.exists(history_path):
            with open(history_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading conversation history: {str(e)}")

    return []
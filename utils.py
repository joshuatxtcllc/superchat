import os
import json
from datetime import datetime

# Custom CSS for styling the chat interface
custom_css = """
<style>
    .main {
        padding: 0 1rem;
        max-width: 60rem;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        background-color: #f9f9f9;
        border-left: 5px solid #e0e0e0;
    }
    .chat-message.user {
        background-color: #f0f7ff;
        border-left: 5px solid #2D87D3;
    }
    .chat-message.assistant {
        background-color: #f9f9f9;
        border-left: 5px solid #9E9E9E;
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        margin-right: 1rem;
    }
    .user-avatar {
        background-color: #2D87D3;
        color: white;
    }
    .assistant-avatar {
        background-color: #9E9E9E;
        color: white;
    }
    .message-content {
        flex-grow: 1;
    }
    .message-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .message-model {
        font-size: 0.8rem;
        color: #666;
        font-style: italic;
    }
    .message-timestamp {
        font-size: 0.8rem;
        color: #888;
    }
    .message-text {
        line-height: 1.5;
    }
    /* Additional styles for model cards */
    .model-card {
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #ffffff;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .model-card h3 {
        margin-top: 0;
        color: #2D87D3;
    }
    .model-card-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 0.5rem 0;
    }
    .model-badge {
        background-color: #f0f7ff;
        color: #2D87D3;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        display: inline-block;
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

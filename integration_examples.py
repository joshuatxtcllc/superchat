
"""
Examples of how to integrate the chat system into existing applications
"""

from model_handler import ModelHandler
from mcp_handler import MCPHandler
from image_generator import ImageGenerator

class ChatIntegration:
    """Simple integration class for existing Python apps"""
    
    def __init__(self):
        self.model_handler = ModelHandler()
        self.mcp_handler = MCPHandler()
        self.image_generator = ImageGenerator()
        self.conversation_history = []
    
    def send_message(self, message, model="gpt-4o", deep_thinking=False):
        """Send a message and get response"""
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Prepare messages for API
        messages_for_api = self.mcp_handler.prepare_messages(self.conversation_history)
        
        # Get response
        response = self.model_handler.get_response(
            messages_for_api, 
            model,
            deep_thinking=deep_thinking
        )
        
        # Add assistant response to history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def generate_image(self, prompt, model="dall-e-3"):
        """Generate an image"""
        return self.image_generator.generate_image(prompt, model)
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_available_models(self):
        """Get list of available models"""
        return list(self.model_handler.models.keys())

# Example usage in Flask app
def flask_integration_example():
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    chat = ChatIntegration()
    
    @app.route('/api/chat', methods=['POST'])
    def chat_endpoint():
        data = request.json
        message = data.get('message')
        model = data.get('model', 'gpt-4o')
        
        response = chat.send_message(message, model)
        return jsonify({'response': response})
    
    return app

# Example usage in Django views
def django_integration_example():
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    import json
    
    chat = ChatIntegration()
    
    @csrf_exempt
    def chat_view(request):
        if request.method == 'POST':
            data = json.loads(request.body)
            message = data.get('message')
            model = data.get('model', 'gpt-4o')
            
            response = chat.send_message(message, model)
            return JsonResponse({'response': response})
    
    return chat_view

# Example standalone usage
if __name__ == "__main__":
    # Simple command-line chat
    chat = ChatIntegration()
    
    print("AI Chat Integration Example")
    print("Type 'quit' to exit")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
        
        response = chat.send_message(user_input)
        print(f"AI: {response}")

import os
import openai
from anthropic import Anthropic
import json

class ModelHandler:
    """
    Handles interactions with different AI models.
    """
    
    def __init__(self):
        # Define available models with their IDs
        # The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # The newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024.
        self.models = {
            "GPT-4o": "gpt-4o",
            "GPT-4o Mini": "gpt-4o-mini",
            "GPT-3.5 Turbo": "gpt-3.5-turbo",
            "Claude 3.5 Sonnet": "claude-3-5-sonnet-20241022",
            "Claude 3 Haiku": "claude-3-haiku-20240307",
            "Claude 3 Sonnet": "claude-3-sonnet-20240229",
            "Claude 3 Opus": "claude-3-opus-20240229",
            "Llama 3 70B": "llama-3-70b-chat",
            "Mistral Large": "mistral-large-latest"
        }
        
        # Model information for each model
        self.model_info = {
            "gpt-4o": {
                "description": "OpenAI's latest multimodal model with enhanced capabilities across text, code, and reasoning tasks.",
                "strengths": [
                    "Superior performance on complex reasoning tasks",
                    "Excellent at coding and technical tasks",
                    "Handles creative writing well",
                    "Multimodal capabilities"
                ],
                "use_cases": [
                    "Programming assistance",
                    "Complex reasoning",
                    "Content creation",
                    "Technical problem-solving"
                ],
                "provider": "openai"
            },
            "gpt-4o-mini": {
                "description": "A smaller, faster version of GPT-4o with good performance at lower cost.",
                "strengths": [
                    "Fast response time",
                    "Good balance of capability and cost",
                    "Handles common tasks well"
                ],
                "use_cases": [
                    "Everyday chat assistance",
                    "Simple reasoning tasks",
                    "Content summarization",
                    "Basic coding help"
                ],
                "provider": "openai"
            },
            "gpt-3.5-turbo": {
                "description": "OpenAI's cost-effective model with good performance for everyday tasks.",
                "strengths": [
                    "Very fast response time",
                    "Cost-effective",
                    "Good for simple to moderate tasks"
                ],
                "use_cases": [
                    "Quick answers to questions",
                    "Simple content generation",
                    "Basic summarization",
                    "Lightweight assistance"
                ],
                "provider": "openai"
            },
            "claude-3-5-sonnet-20241022": {
                "description": "Anthropic's latest model with excellent reasoning and conversation abilities.",
                "strengths": [
                    "Strong reasoning ability",
                    "Nuanced understanding of complex topics",
                    "Long context window",
                    "Balanced performance across tasks"
                ],
                "use_cases": [
                    "Long-form content analysis",
                    "Research assistance",
                    "Thoughtful conversations",
                    "Detailed document analysis"
                ],
                "provider": "anthropic"
            },
            "claude-3-haiku-20240307": {
                "description": "Anthropic's fastest model for efficient, responsive interactions.",
                "strengths": [
                    "Very fast responses",
                    "Cost-effective",
                    "Good for straightforward tasks"
                ],
                "use_cases": [
                    "Quick Q&A",
                    "Simple content creation",
                    "Fast feedback",
                    "Lightweight assistance"
                ],
                "provider": "anthropic"
            },
            "claude-3-sonnet-20240229": {
                "description": "Balanced Anthropic model with good performance across many tasks.",
                "strengths": [
                    "Well-rounded capabilities",
                    "Good balance of speed and performance",
                    "Handles most common tasks effectively"
                ],
                "use_cases": [
                    "General content creation",
                    "Research assistance",
                    "Thoughtful conversations",
                    "Document analysis"
                ],
                "provider": "anthropic"
            },
            "claude-3-opus-20240229": {
                "description": "Anthropic's most powerful model for sophisticated, nuanced tasks.",
                "strengths": [
                    "Exceptional reasoning ability",
                    "Handles complex, nuanced topics well",
                    "Excellent at detailed analysis",
                    "Strong at understanding context"
                ],
                "use_cases": [
                    "Complex reasoning",
                    "Nuanced content creation",
                    "In-depth research assistance",
                    "Complex problem-solving"
                ],
                "provider": "anthropic"
            },
            "llama-3-70b-chat": {
                "description": "Meta's open model with strong capabilities across various tasks.",
                "strengths": [
                    "Open-weights model",
                    "Strong general capabilities",
                    "Good at coding and reasoning"
                ],
                "use_cases": [
                    "General assistance",
                    "Coding help",
                    "Content creation",
                    "Research support"
                ],
                "provider": "meta"
            },
            "mistral-large-latest": {
                "description": "Mistral AI's powerful model with strong reasoning and coding capabilities.",
                "strengths": [
                    "Excellent reasoning",
                    "Strong coding abilities",
                    "Good at following instructions"
                ],
                "use_cases": [
                    "Technical assistance",
                    "Coding and development",
                    "Complex problem-solving",
                    "Research support"
                ],
                "provider": "mistral"
            }
        }
    
    def get_model_keys(self):
        """Returns a list of model names (keys)"""
        return list(self.models.keys())
    
    def get_model_info(self, model_id):
        """Returns information about a specific model"""
        return self.model_info.get(model_id, {
            "description": "Model information not available",
            "strengths": ["Information not available"],
            "use_cases": ["Information not available"],
            "provider": "unknown"
        })
    
    def get_response(self, messages, model_id, deep_thinking=False, uploaded_files=None):
        """Get a response from the specified AI model"""
        try:
            # Add file context if files are uploaded
            if uploaded_files:
                file_context = self._process_uploaded_files(uploaded_files)
                if file_context:
                    # Add file information to the last user message
                    if messages and messages[-1]["role"] == "user":
                        messages[-1]["content"] += f"\n\n[Uploaded files context: {file_context}]"
            
            # Add deep thinking prompt if enabled
            if deep_thinking:
                thinking_prompt = "\n\nPlease show your reasoning process step by step before providing your final answer. Use a 'Thinking:' section to show your thought process transparently."
                
                # Add screen analysis guidance if screen capture detected
                if uploaded_files:
                    for file in uploaded_files:
                        if 'screen-capture' in file.name.lower() or 'screenshot' in file.name.lower():
                            thinking_prompt += "\n\nFor screen captures, please analyze: UI elements, applications visible, potential workflows, any text content, layout patterns, and provide actionable insights about what's shown."
                            break
                
                if messages and messages[-1]["role"] == "user":
                    messages[-1]["content"] += thinking_prompt
            
            # Get the provider from model info
            model_info = self.get_model_info(model_id)
            provider = model_info.get("provider", "unknown")
            
            if provider == "openai":
                return self._get_openai_response(messages, model_id)
            elif provider == "anthropic":
                return self._get_anthropic_response(messages, model_id)
            elif provider == "meta":
                return self._get_meta_response(messages, model_id)
            elif provider == "mistral":
                return self._get_mistral_response(messages, model_id)
            else:
                return f"Unsupported model: {model_id}"
        
        except Exception as e:
            return f"Error getting response: {str(e)}"
    
    def _process_uploaded_files(self, uploaded_files):
        """Process uploaded files and return context string"""
        file_info = []
        
        for file in uploaded_files:
            try:
                file_type = file.type
                file_name = file.name
                
                if file_type.startswith('text/') or file_name.endswith('.txt'):
                    # Read text files
                    content = file.read().decode('utf-8')[:2000]  # Limit to first 2000 chars
                    file_info.append(f"Text file '{file_name}': {content[:500]}{'...' if len(content) > 500 else ''}")
                
                elif file_type.startswith('image/'):
                    # For images, provide detailed context
                    if 'screen-capture' in file_name.lower() or 'screenshot' in file_name.lower():
                        file_info.append(f"Screen capture '{file_name}' ({file_type}) - This appears to be a screenshot that may contain UI elements, applications, or desktop content for analysis")
                    else:
                        file_info.append(f"Image file '{file_name}' ({file_type}) uploaded")
                
                elif file_name.endswith('.csv'):
                    # Read CSV files
                    import csv
                    import io
                    content = file.read().decode('utf-8')
                    csv_reader = csv.reader(io.StringIO(content))
                    rows = list(csv_reader)[:10]  # First 10 rows
                    file_info.append(f"CSV file '{file_name}' with {len(rows)} rows (showing first 10): {str(rows)}")
                
                elif file_name.endswith('.json'):
                    # Read JSON files
                    content = file.read().decode('utf-8')
                    json_data = json.loads(content)
                    file_info.append(f"JSON file '{file_name}': {str(json_data)[:500]}{'...' if len(str(json_data)) > 500 else ''}")
                
                else:
                    # For other file types, just note the presence
                    file_info.append(f"File '{file_name}' ({file_type}) uploaded")
                
                # Reset file pointer for potential future reads
                file.seek(0)
                
            except Exception as e:
                file_info.append(f"Error processing file '{file.name}': {str(e)}")
        
        return " | ".join(file_info) if file_info else None
    
    def _get_openai_response(self, messages, model_id):
        """Get a response from OpenAI models"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "OpenAI API key not found. Please add your API key in the settings."
        
        try:
            client = openai.OpenAI(api_key=api_key)
            
            # Convert messages to OpenAI format if they aren't already
            openai_messages = []
            for msg in messages:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    openai_messages.append(msg)
                else:
                    # Handle other formats or unexpected message structures
                    openai_messages.append({"role": "user", "content": str(msg)})
            
            response = client.chat.completions.create(
                model=model_id,
                messages=openai_messages,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"OpenAI API Error: {str(e)}"
    
    def _get_anthropic_response(self, messages, model_id):
        """Get a response from Anthropic models"""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return "Anthropic API key not found. Please add your API key in the settings."
        
        try:
            client = Anthropic(api_key=api_key)
            
            # Convert messages to Anthropic format
            anthropic_messages = []
            for msg in messages:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    # Map OpenAI roles to Anthropic roles
                    role = "user" if msg["role"] == "user" else "assistant"
                    anthropic_messages.append({"role": role, "content": msg["content"]})
            
            response = client.messages.create(
                model=model_id,
                messages=anthropic_messages,
                max_tokens=1000,
            )
            
            return response.content[0].text
        
        except Exception as e:
            return f"Anthropic API Error: {str(e)}"
    
    def _get_meta_response(self, messages, model_id):
        """Get a response from Meta AI models"""
        # For now, we'll use OpenAI API as a fallback with a note
        return self._get_openai_response(messages, "gpt-4o") + "\n\n[Note: Meta AI integration is simulated using OpenAI's API. In a production environment, you would use Meta's API directly.]"
    
    def _get_mistral_response(self, messages, model_id):
        """Get a response from Mistral AI models"""
        # For now, we'll use OpenAI API as a fallback with a note
        return self._get_openai_response(messages, "gpt-4o") + "\n\n[Note: Mistral AI integration is simulated using OpenAI's API. In a production environment, you would use Mistral's API directly.]"

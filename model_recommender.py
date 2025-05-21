import os
import json
import openai
from model_handler import ModelHandler

class ModelRecommender:
    """
    Recommends the optimal AI model based on user task descriptions.
    Uses the capabilities of GPT-4o to analyze the task and suggest the best model.
    """
    
    def __init__(self):
        # Initialize the model handler to access model information
        self.model_handler = ModelHandler()
        
        # Template for the recommendation prompt
        self.recommendation_template = """
You are an AI model recommendation expert. Your task is to analyze the user's description and recommend 
the most suitable AI model for their needs.

Available models:
{model_details}

User's task description:
"{task_description}"

Based on the task description and the model capabilities, recommend the most suitable model.
Consider factors like:
- Task complexity
- Need for reasoning or creativity
- Cost-effectiveness
- Speed requirements
- Specialized capabilities needed

Provide your recommendation in JSON format with the following structure:
{{
    "model_name": "The recommended model name (exactly as listed above)",
    "explanation": "A detailed explanation of why this model is the best fit for the task (3-5 sentences)",
    "alternative_models": ["Model1", "Model2"],
    "alternative_explanation": "Brief explanation of when to consider the alternatives"
}}
"""
        
    def get_recommendation(self, task_description):
        """
        Analyzes the user's task description and recommends the optimal model.
        """
        # Get the API key
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {
                "model_name": "GPT-4o",
                "explanation": "Unable to provide a personalized recommendation without OpenAI API key. GPT-4o is recommended as a default as it has strong general capabilities.",
                "alternative_models": ["Claude 3.5 Sonnet", "GPT-4o Mini"],
                "alternative_explanation": "Consider Claude 3.5 Sonnet for long-form content or GPT-4o Mini for faster, more cost-effective responses."
            }
        
        # Build model details information
        model_details = ""
        for model_name, model_id in self.model_handler.models.items():
            model_info = self.model_handler.get_model_info(model_id)
            model_details += f"- {model_name}: {model_info['description']}\n"
            model_details += f"  Strengths: {', '.join(model_info['strengths'])}\n"
            model_details += f"  Use cases: {', '.join(model_info['use_cases'])}\n\n"
        
        # Format the prompt
        prompt = self.recommendation_template.format(
            model_details=model_details,
            task_description=task_description
        )
        
        try:
            # Create OpenAI client
            client = openai.OpenAI(api_key=api_key)
            
            # Make the recommendation request
            response = client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o as it's the newest OpenAI model
                messages=[
                    {"role": "system", "content": "You are an AI model recommendation expert."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,  # Lower temperature for more consistent recommendations
            )
            
            # Parse the response
            recommendation = response.choices[0].message.content
            
            # Convert the JSON string to a Python dict
            try:
                recommendation_data = json.loads(recommendation)
                return recommendation_data
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "model_name": "GPT-4o",
                    "explanation": "Unable to parse the recommendation properly. GPT-4o is recommended as a default as it has strong general capabilities.",
                    "alternative_models": ["Claude 3.5 Sonnet", "GPT-4o Mini"],
                    "alternative_explanation": "Consider Claude 3.5 Sonnet for long-form content or GPT-4o Mini for faster, more cost-effective responses."
                }
                
        except Exception as e:
            # Fallback recommendation with error info
            return {
                "model_name": "GPT-4o",
                "explanation": f"Error during recommendation: {str(e)}. GPT-4o is recommended as a default as it has strong general capabilities.",
                "alternative_models": ["Claude 3.5 Sonnet", "GPT-4o Mini"],
                "alternative_explanation": "Consider Claude 3.5 Sonnet for long-form content or GPT-4o Mini for faster, more cost-effective responses."
            }

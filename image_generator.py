
import os
import requests
import base64
from io import BytesIO
from PIL import Image
import openai

class ImageGenerator:
    """
    Handles image generation using various AI models.
    """
    
    def __init__(self):
        self.available_models = {
            "DALL-E 3": "dall-e-3",
            "DALL-E 2": "dall-e-2",
            "Stable Diffusion": "stable-diffusion"  # Placeholder for future integration
        }
    
    def generate_image(self, prompt, model="dall-e-3", size="1024x1024", quality="standard", style="vivid"):
        """Generate an image using the specified model"""
        
        if model in ["dall-e-2", "dall-e-3"]:
            return self._generate_dalle_image(prompt, model, size, quality, style)
        elif model == "stable-diffusion":
            return self._generate_stable_diffusion_image(prompt)
        else:
            return {"error": f"Unsupported model: {model}"}
    
    def _generate_dalle_image(self, prompt, model, size, quality, style):
        """Generate image using OpenAI's DALL-E"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {"error": "OpenAI API key not found. Please add your OPENAI_API_KEY to Secrets."}
        
        try:
            client = openai.OpenAI(api_key=api_key)
            
            # DALL-E 3 parameters
            if model == "dall-e-3":
                response = client.images.generate(
                    model=model,
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    style=style,
                    n=1
                )
            else:  # DALL-E 2
                response = client.images.generate(
                    model=model,
                    prompt=prompt,
                    size=size,
                    n=1
                )
            
            image_url = response.data[0].url
            
            return {
                "success": True,
                "image_url": image_url,
                "model": model,
                "prompt": prompt,
                "size": size
            }
        
        except Exception as e:
            return {"error": f"DALL-E API Error: {str(e)}"}
    
    def _generate_stable_diffusion_image(self, prompt):
        """Placeholder for Stable Diffusion integration"""
        return {"error": "Stable Diffusion integration not yet implemented. Use DALL-E models for now."}
    
    def download_image(self, image_url):
        """Download image from URL and return as PIL Image"""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            return image
        except Exception as e:
            return None

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

    def generate_image(self, prompt, model="dall-e-3", size="1024x1024", quality="standard", style="vivid", reference_image_url=None):
        """Generate an image using the specified model"""

        if model in ["dall-e-2", "dall-e-3"]:
            return self._generate_dalle_image(prompt, model, size, quality, style, reference_image_url)
        elif model == "stable-diffusion":
            return self._generate_stable_diffusion_image(prompt)
        else:
            return {"error": f"Unsupported model: {model}"}

    def _generate_dalle_image(self, prompt, model, size, quality, style, reference_image_url):
        """Generate image using OpenAI's DALL-E"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {"error": "OpenAI API key not found. Please add your OPENAI_API_KEY to Secrets."}

        try:
            client = openai.OpenAI(api_key=api_key)

            # Add reference image info to prompt if provided
            if reference_image_url:
                prompt = f"{prompt}\n\nReference image style: {reference_image_url}"

            if model == "dall-e-3":
                # Check usage limits before generating
                from usage_monitor import usage_monitor
                service_status = usage_monitor.is_service_blocked()
                if service_status['any_blocked']:
                    return {
                        'success': False,
                        'error_message': 'Image generation temporarily unavailable due to usage limits.',
                        'image_url': None
                    }

                response = client.images.generate(
                    model=model,
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    style=style,
                    n=1
                )

                # Track image generation usage
                estimated_cost = 0.04 if quality == "standard" else 0.08  # DALL-E-3 pricing
                usage_monitor.track_usage("image", 1, estimated_cost)
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

    def improve_prompt(self, user_prompt):
        """Improve user's image prompt using AI"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {"error": "OpenAI API key not found. Please add your OPENAI_API_KEY to Secrets."}

        try:
            client = openai.OpenAI(api_key=api_key)

            improvement_prompt = f"""
You are an expert at crafting detailed, effective prompts for AI image generation. 
Transform the user's basic prompt into a highly detailed, specific prompt that will generate better images.

Original prompt: "{user_prompt}"

Improve this prompt by:
1. Adding specific artistic style details
2. Including lighting and composition information
3. Specifying colors, textures, and mood
4. Adding technical photography/art terms
5. Being more descriptive about subjects and settings
6. Keeping the core intent but making it much more detailed

Return only the improved prompt, nothing else.
"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert prompt engineer for AI image generation."},
                    {"role": "user", "content": improvement_prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            improved_prompt = response.choices[0].message.content.strip()

            return {
                "success": True,
                "improved_prompt": improved_prompt,
                "original_prompt": user_prompt
            }

        except Exception as e:
            return {"error": f"Prompt improvement error: {str(e)}"}

    def download_image(self, image_url):
        """Download image from URL and return as PIL Image"""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            return image
        except Exception as e:
            return None
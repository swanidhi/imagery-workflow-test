"""
Image Generator for AI Product Imagery Workflow

Handles image generation using Gemini Flash Image or Pro Image models,
with proper output file naming and non-overwrite logic.
"""

import os
import re
from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("Warning: google-genai not installed. Run: pip install google-genai")


class ImageGenerator:
    """Generates product images using Gemini Image models."""
    
    # Model-specific settings keyed by ACTUAL API model ID
    # Config uses these names directly - no aliases!
    MODEL_CONFIGS = {
        'gemini-2.0-flash-exp': {
            'supports_negative_prompt': True,
            'use_imagen_api': False,
        },
        'imagen-3.0-generate-002': {
            'supports_negative_prompt': False,
            'use_imagen_api': True,
        }
        # Any unknown model will use defaults
    }
    
    def __init__(
        self, 
        model_name: str = "gemini-2.5-flash-image",
        output_base: str = "./output",
        aspect_ratio: str = "1:1",
        counter_start: int = 101,
        counter_max: int = 110
    ):
        """
        Initialize image generator.
        
        Args:
            model_name: Which model to use for generation
            output_base: Base directory for output images
            aspect_ratio: Image aspect ratio (default 1:1)
            counter_start: Starting counter for image naming (default 101)
            counter_max: Maximum counter value (default 110)
        """
        self.model_name = model_name
        self.output_base = Path(output_base)
        self.aspect_ratio = aspect_ratio
        self.counter_start = counter_start
        self.counter_max = counter_max
        
        self._client = None
        self._init_client()
    
    def _init_client(self) -> None:
        """Initialize the Gemini client."""
        if not GENAI_AVAILABLE:
            return
        
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            print("Warning: GEMINI_API_KEY not set in environment")
            return
        
        self._client = genai.Client(api_key=api_key)
    
    def _get_next_counter(self, tranche_dir: Path, cupid_name: str) -> int:
        """
        Find next available counter for a cupidName to avoid overwriting.
        
        Args:
            tranche_dir: Path to tranche output directory
            cupid_name: Product cupidName
            
        Returns:
            Next available counter (101-110)
        """
        pattern = re.compile(rf"{re.escape(cupid_name)}_l(\d+)\.jpg")
        existing_counters = set()
        
        if tranche_dir.exists():
            for file_path in tranche_dir.glob(f"{cupid_name}_l*.jpg"):
                match = pattern.match(file_path.name)
                if match:
                    existing_counters.add(int(match.group(1)))
        
        # Find next available counter
        for counter in range(self.counter_start, self.counter_max + 1):
            if counter not in existing_counters:
                return counter
        
        # All counters used - return max+1 (will overflow naming but won't overwrite)
        return max(existing_counters) + 1 if existing_counters else self.counter_start
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        reference_images: Optional[list[bytes]] = None
    ) -> Optional[bytes]:
        """
        Generate an image using the configured model.
        
        Args:
            prompt: Positive prompt for generation
            negative_prompt: Negative prompt (if supported)
            reference_images: Optional reference images for context
            
        Returns:
            Generated image bytes or None if failed
        """
        if not self._client:
            print("Error: Gemini client not initialized")
            return None
        
        try:
            model_config = self.MODEL_CONFIGS.get(self.model_name, {})
            # model_name IS the actual API model ID - use it directly
            model_id = self.model_name
            
            # Build the content for generation
            contents = [prompt]
            
            # Add reference images if provided
            if reference_images:
                for img_bytes in reference_images[:2]:  # Limit to 2 reference images
                    image_part = types.Part.from_bytes(
                        data=img_bytes,
                        mime_type="image/jpeg"
                    )
                    contents.append(image_part)
            
            # Configure generation
            config = types.GenerateContentConfig(
                response_modalities=['IMAGE', 'TEXT'],
            )
            
            # Generate
            response = self._client.models.generate_content(
                model=model_id,
                contents=contents,
                config=config
            )
            
            # Extract image from response
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    return part.inline_data.data
            
            print("No image generated in response")
            return None
            
        except Exception as e:
            print(f"Error generating image: {e}")
            return None
    
    def save_image(
        self,
        image_bytes: bytes,
        tranche: str,
        cupid_name: str,
        prompt: str = "",
        negative_prompt: str = "",
        metadata: Optional[dict] = None
    ) -> tuple[str, str]:
        """
        Save generated image with proper naming convention and audit log.
        
        Args:
            image_bytes: Generated image data
            tranche: Product tranche (e.g., "Tranche 1")
            cupid_name: Product cupidName
            prompt: The positive prompt used (for audit)
            negative_prompt: The negative prompt used (for audit)
            metadata: Additional metadata to save
            
        Returns:
            Tuple of (image_path, metadata_path)
        """
        import json
        from datetime import datetime
        
        # Create tranche directory
        tranche_dir = self.output_base / tranche
        tranche_dir.mkdir(parents=True, exist_ok=True)
        
        # Get next counter
        counter = self._get_next_counter(tranche_dir, cupid_name)
        
        # Build filenames
        # Build filenames and paths
        # Structure:
        # output/Tranche 1/cupid_l101.jpg
        # output/logs/Tranche 1/cupid_l101.json
        
        base_filename = f"{cupid_name}_l{counter}"
        image_path = tranche_dir / f"{base_filename}.jpg"
        
        # Logs directory parallel to tranche dir nature
        # If tranche_dir is "output/Tranche 1", logs_dir is "output/logs/Tranche 1"
        logs_base = self.output_base / "logs"
        logs_tranche_dir = logs_base / tranche
        logs_tranche_dir.mkdir(parents=True, exist_ok=True)
        
        metadata_path = logs_tranche_dir / f"{base_filename}.json"
        
        # Save image
        with open(image_path, 'wb') as f:
            f.write(image_bytes)
        
        # Save audit metadata
        audit_data = {
            "cupid_name": cupid_name,
            "tranche": tranche,
            "counter": counter,
            "image_file": f"{base_filename}.jpg",
            "generated_at": datetime.now().isoformat(),
            "model": self.model_name,  # The actual API model ID from config
            "model_id": self.model_name,  # Same value - what you configure is what's used
            "aspect_ratio": self.aspect_ratio,
            "prompts": {
                "positive": prompt,
                "negative": negative_prompt
            }
        }
        
        # Merge additional metadata if provided
        if metadata:
            audit_data.update(metadata)
        
        with open(metadata_path, 'w') as f:
            json.dump(audit_data, f, indent=2)
        
        return str(image_path), str(metadata_path)
    
    def generate_and_save(
        self,
        prompt: str,
        negative_prompt: str,
        tranche: str,
        cupid_name: str,
        reference_images: Optional[list[bytes]] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Generate and save an image in one step with full audit trail.
        
        Returns:
            Dict with 'success', 'path', 'metadata_path', and 'error' keys
        """
        result = {
            'success': False,
            'path': None,
            'metadata_path': None,
            'error': None,
            'prompt_used': prompt[:200] + '...' if len(prompt) > 200 else prompt
        }
        
        # Generate
        image_bytes = self.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            reference_images=reference_images
        )
        
        if not image_bytes:
            result['error'] = 'Image generation failed'
            return result
        
        # Save with audit log
        try:
            image_path, metadata_path = self.save_image(
                image_bytes=image_bytes,
                tranche=tranche,
                cupid_name=cupid_name,
                prompt=prompt,
                negative_prompt=negative_prompt,
                metadata=metadata
            )
            result['success'] = True
            result['path'] = image_path
            result['metadata_path'] = metadata_path
        except Exception as e:
            result['error'] = f'Failed to save: {e}'
        
        return result


def create_image_generator(
    model_name: str = "gemini-2.5-flash-image",
    config: Optional[dict] = None
) -> ImageGenerator:
    """Factory function to create ImageGenerator from config."""
    if config:
        return ImageGenerator(
            model_name=config.get('models', {}).get('image_generation', model_name),
            output_base=config.get('output', {}).get('base_path', './output'),
            aspect_ratio=config.get('image_settings', {}).get('aspect_ratio', '1:1'),
            counter_start=config.get('output', {}).get('counter_start', 101),
            counter_max=config.get('output', {}).get('counter_max', 110)
        )
    return ImageGenerator(model_name=model_name)


if __name__ == "__main__":
    # Quick test
    generator = create_image_generator()
    
    print(f"Model: {generator.model_name}")
    print(f"Output base: {generator.output_base}")
    print(f"Counter range: {generator.counter_start}-{generator.counter_max}")
    
    # Test counter logic
    test_dir = Path("./output/Tranche 1")
    test_cupid = "test_product_123"
    next_counter = generator._get_next_counter(test_dir, test_cupid)
    print(f"Next counter for {test_cupid}: {next_counter}")

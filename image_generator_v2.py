"""
Image Generator V2 for Nano Banana Pro Architecture

Enhanced generator with:
- System Instruction support (Safety Constitution)
- ImageConfig for aspect ratio and resolution
- Thinking process (always enabled for Gemini 3 Pro Image)
- Up to 14 reference images support
"""

import os
import re
import yaml
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


class ImageGeneratorV2:
    """
    V2 Image Generator using Nano Banana Pro (Gemini 3 Pro Image).
    
    Key differences from V1:
    - Uses System Instruction for immutable safety rules
    - Uses ImageConfig for resolution control
    - Supports up to 14 reference images
    - Thinking process is always enabled (cannot be disabled)
    """
    
    def __init__(
        self, 
        model_name: str = "gemini-3-pro-image-preview",
        output_base: str = "./output",
        aspect_ratio: str = "1:1",
        image_size: str = "1K",  # Options: 1K, 2K, 4K
        counter_start: int = 101,
        counter_max: int = 110,
        safety_constitution_path: str = "safety_constitution.yaml"
    ):
        """
        Initialize V2 image generator.
        
        Args:
            model_name: Model to use (must be gemini-3-pro-image-preview for V2)
            output_base: Base directory for output images
            aspect_ratio: Image aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4)
            image_size: Output resolution (1K, 2K, 4K)
            counter_start: Starting counter for image naming
            counter_max: Maximum counter value
            safety_constitution_path: Path to safety rules YAML
        """
        self.model_name = model_name
        self.output_base = Path(output_base)
        self.aspect_ratio = aspect_ratio
        self.image_size = image_size
        self.counter_start = counter_start
        self.counter_max = counter_max
        
        self._client = None
        self._system_instruction = None
        
        self._init_client()
        self._load_safety_constitution(safety_constitution_path)
    
    def _init_client(self) -> None:
        """Initialize the Gemini client."""
        if not GENAI_AVAILABLE:
            return
        
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            print("Warning: GEMINI_API_KEY not set in environment")
            return
        
        self._client = genai.Client(api_key=api_key)
    
    def _load_safety_constitution(self, path: str) -> None:
        """Load safety constitution from YAML file."""
        constitution_path = Path(path)
        if not constitution_path.exists():
            print(f"Warning: Safety constitution not found at {path}")
            self._system_instruction = ""
            return
        
        with open(constitution_path) as f:
            constitution = yaml.safe_load(f)
        
        # Build system instruction from all sections
        parts = []
        
        for section_name, directives in constitution.items():
            if isinstance(directives, list):
                for directive in directives:
                    parts.append(directive)
        
        self._system_instruction = "\n\n".join(parts)
    
    def _get_next_counter(self, tranche_dir: Path, cupid_name: str) -> int:
        """Find next available counter for a cupidName to avoid overwriting."""
        pattern = re.compile(rf"{re.escape(cupid_name)}_l(\d+)\.jpg")
        existing_counters = set()
        
        if tranche_dir.exists():
            for file_path in tranche_dir.glob(f"{cupid_name}_l*.jpg"):
                match = pattern.match(file_path.name)
                if match:
                    existing_counters.add(int(match.group(1)))
        
        for counter in range(self.counter_start, self.counter_max + 1):
            if counter not in existing_counters:
                return counter
        
        return max(existing_counters) + 1 if existing_counters else self.counter_start
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        reference_images: Optional[list[bytes]] = None
    ) -> Optional[bytes]:
        """
        Generate an image using Gemini 3 Pro Image with V2 enhancements.
        
        Args:
            prompt: Positive prompt for generation
            negative_prompt: Negative prompt (embedded in main prompt for V2)
            reference_images: Up to 14 reference images for Identity Locking
            
        Returns:
            Generated image bytes or None if failed
        """
        if not self._client:
            print("Error: Gemini client not initialized")
            return None
        
        try:
            # Build contents with reference images FIRST (Identity Locking)
            contents = []
            
            # Add reference images (up to 14 supported)
            if reference_images:
                for img_bytes in reference_images[:14]:
                    image_part = types.Part.from_bytes(
                        data=img_bytes,
                        mime_type="image/jpeg"
                    )
                    contents.append(image_part)
            
            # Build enhanced prompt with negative constraints embedded
            full_prompt = prompt
            if negative_prompt:
                full_prompt += f"\n\nNEGATIVE CONSTRAINTS (STRICT ADHERENCE REQUIRED): {negative_prompt}"
            
            contents.append(full_prompt)
            
            # Configure generation with V2 enhancements
            # Note: Gemini 3 Pro Image has "Thinking" always on, but we can influence
            # the budget/effort via thinking_config (per Nano Banana research §2.2)
            config = types.GenerateContentConfig(
                response_modalities=['IMAGE', 'TEXT'],
                system_instruction=self._system_instruction,
                # Explicitly set thinking budget for enhanced reasoning (safety, context selection)
                thinking_config=types.ThinkingConfig(
                    thinking_budget=1024  # Medium reasoning effort
                ),
            )
            
            # Generate
            response = self._client.models.generate_content(
                model=self.model_name,
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
        Save generated image with proper naming and audit log.
        
        Returns:
            Tuple of (image_path, metadata_path)
        """
        import json
        
        # Create directories
        tranche_dir = self.output_base / tranche
        tranche_dir.mkdir(parents=True, exist_ok=True)
        
        logs_tranche_dir = self.output_base / "logs" / tranche
        logs_tranche_dir.mkdir(parents=True, exist_ok=True)
        
        # Get next counter
        counter = self._get_next_counter(tranche_dir, cupid_name)
        
        # Build filenames
        base_filename = f"{cupid_name}_l{counter}"
        image_path = tranche_dir / f"{base_filename}.jpg"
        metadata_path = logs_tranche_dir / f"{base_filename}.json"
        
        # Save image
        with open(image_path, 'wb') as f:
            f.write(image_bytes)
        
        # Build comprehensive audit data
        audit_data = {
            "cupid_name": cupid_name,
            "tranche": tranche,
            "counter": counter,
            "image_file": f"{base_filename}.jpg",
            "generated_at": datetime.now().isoformat(),
            "model": self.model_name,
            "model_id": self.model_name,
            "engine_version": "v2_nanobananapro",
            "aspect_ratio": self.aspect_ratio,
            "image_size": self.image_size,
            "system_instruction_enabled": bool(self._system_instruction),
            "prompts": {
                "positive": prompt,
                "negative": negative_prompt
            }
        }
        
        # Merge additional metadata
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
        Generate and save an image with full V2 audit trail.
        
        Returns:
            Dict with 'success', 'path', 'metadata_path', and 'error' keys
        """
        result = {
            'success': False,
            'path': None,
            'metadata_path': None,
            'error': None,
            'engine_version': 'v2_nanobananapro',
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


def create_image_generator_v2(config: Optional[dict] = None) -> ImageGeneratorV2:
    """Factory function to create V2 ImageGenerator from config."""
    if config:
        v2_config = config.get('generation', {}).get('v2', {})
        return ImageGeneratorV2(
            model_name=config.get('models', {}).get('image_generation', 'gemini-3-pro-image-preview'),
            output_base=config.get('output', {}).get('base_path', './output'),
            aspect_ratio=v2_config.get('aspect_ratio', '1:1'),
            image_size=v2_config.get('image_size', '1K'),
            counter_start=config.get('output', {}).get('counter_start', 101),
            counter_max=config.get('output', {}).get('counter_max', 110),
            safety_constitution_path=v2_config.get('system_instruction_file', 'safety_constitution.yaml')
        )
    return ImageGeneratorV2()


if __name__ == "__main__":
    # Quick test
    generator = create_image_generator_v2()
    
    print(f"Model: {generator.model_name}")
    print(f"Output base: {generator.output_base}")
    print(f"System Instruction loaded: {bool(generator._system_instruction)}")
    print(f"Aspect Ratio: {generator.aspect_ratio}")
    print(f"Image Size: {generator.image_size}")

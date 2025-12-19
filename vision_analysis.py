"""
Vision Analysis Module for AI Product Imagery Workflow

Analyzes ghost images using Gemini Vision to extract visible features,
preventing hallucination of features not visible in the product images.
"""

import base64
import os
import requests
from typing import Optional
from pathlib import Path

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("Warning: google-genai not installed. Run: pip install google-genai")


class VisionAnalyzer:
    """Analyzes product ghost images to extract visible features."""
    
    ANALYSIS_PROMPT = """Analyze this product image carefully. This is a firearm product photograph.

Your task is to describe ONLY what is VISIBLY present in the image - do not assume or infer features that cannot be clearly seen.

Please provide a structured analysis:

1. PRODUCT TYPE: What type of firearm is this? (pistol, rifle, shotgun, etc.)

2. VISIBLE PHYSICAL FEATURES:
   - Frame/receiver material and color (if distinguishable)
   - Grip style and texture (if visible)
   - Barrel characteristics (length estimate, finish)
   - Sights (type if visible)
   - Any visible accessories or attachments
   - Overall finish/color

3. VISIBLE CONDITION/QUALITY INDICATORS:
   - Surface finish quality
   - Any visible branding/logos/text
   - Notable design elements

4. CAMERA ANGLE & PRESENTATION:
   - How is the product positioned?
   - What angle is shown?
   - What parts of the product are clearly visible vs obscured?

5. FEATURES THAT CANNOT BE VERIFIED FROM THIS IMAGE:
   - List any features that typically exist but are not visible in this specific image

Be conservative - if something is partially visible or unclear, note that uncertainty.
"""

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """
        Initialize vision analyzer.
        
        Args:
            model_name: Gemini model to use for vision analysis
        """
        self.model_name = model_name
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
    
    def fetch_image(self, url: str) -> Optional[bytes]:
        """
        Fetch image from URL.
        
        Args:
            url: Image URL (Scene7)
            
        Returns:
            Image bytes or None if failed
        """
        try:
            # Scene7 URLs may need size parameter for optimal quality
            if 'scene7.com' in url and '?' not in url:
                url = f"{url}?wid=1024&hei=1024&fmt=jpg"
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error fetching image from {url}: {e}")
            return None
    
    def analyze_image(self, image_bytes: bytes) -> dict:
        """
        Analyze a single image using Gemini Vision.
        
        Args:
            image_bytes: Raw image data
            
        Returns:
            Analysis dict with visible features
        """
        if not self._client:
            return {'error': 'Gemini client not initialized', 'raw_analysis': ''}
        
        try:
            # Create image part
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg"
            )
            
            # Generate content
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=[self.ANALYSIS_PROMPT, image_part]
            )
            
            analysis_text = response.text
            
            return {
                'raw_analysis': analysis_text,
                'success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'raw_analysis': '',
                'success': False
            }
    
    def analyze_ghost_images(
        self, 
        image_urls: list[str], 
        product_specs: dict
    ) -> dict:
        """
        Analyze all ghost images and compile visible features.
        
        Args:
            image_urls: List of Scene7 image URLs
            product_specs: Product specifications from data layer
            
        Returns:
            Compiled analysis with visible features
        """
        if not image_urls:
            return {
                'visible_features': [],
                'analyses': [],
                'error': 'No ghost images available'
            }
        
        analyses = []
        all_visible_features = []
        
        # Analyze primary image (first one) and optionally one more
        urls_to_analyze = image_urls[:2]  # Analyze up to 2 images
        
        for url in urls_to_analyze:
            image_bytes = self.fetch_image(url)
            if image_bytes:
                analysis = self.analyze_image(image_bytes)
                analyses.append({
                    'url': url,
                    'analysis': analysis
                })
        
        # Compile visible features from analyses
        compiled = self._compile_visible_features(analyses, product_specs)
        
        return {
            'visible_features': compiled['visible'],
            'unverified_features': compiled['unverified'],
            'analyses': analyses,
            'image_count_analyzed': len(analyses)
        }
    
    def _compile_visible_features(
        self, 
        analyses: list[dict], 
        product_specs: dict
    ) -> dict:
        """
        Compile visible vs unverified features based on analyses.
        
        This is the anti-hallucination logic - we only include features
        that can be verified from the images.
        """
        # Extract text features from all analyses
        combined_text = " ".join([
            a.get('analysis', {}).get('raw_analysis', '')
            for a in analyses
        ]).lower()
        
        visible = []
        unverified = []
        
        # Known visible attributes from typical product photos
        visible_attribute_keywords = {
            'Finish': ['black', 'silver', 'stainless', 'nickel', 'fde', 'tan', 'grey'],
            'Grip': ['textured', 'stippled', 'rubber', 'polymer', 'wood'],
            'Frame Material': ['polymer', 'steel', 'alloy', 'aluminum'],
            'Barrel Length': ['barrel'],  # General presence
            'Sights': ['sight', 'fiber optic', 'iron sight', 'rear sight', 'front sight'],
            'Optic Ready': ['optic', 'cut', 'mounting'],
        }
        
        # Check specifications against visible keywords
        specs = product_specs.get('specifications', {})
        
        for spec_key, spec_value in specs.items():
            spec_lower = str(spec_value).lower()
            keywords = visible_attribute_keywords.get(spec_key, [spec_lower[:5]])
            
            # Check if any keyword appears in the analysis
            if any(kw in combined_text for kw in keywords):
                visible.append({
                    'attribute': spec_key,
                    'value': spec_value,
                    'verified': True
                })
            else:
                unverified.append({
                    'attribute': spec_key,
                    'value': spec_value,
                    'reason': 'Not visible in analyzed images'
                })
        
        return {
            'visible': visible,
            'unverified': unverified
        }


def create_vision_analyzer(model_name: str = "gemini-2.5-flash") -> VisionAnalyzer:
    """Factory function to create VisionAnalyzer."""
    return VisionAnalyzer(model_name)


if __name__ == "__main__":
    # Test with a sample URL
    analyzer = create_vision_analyzer()
    
    test_url = "https://academy.scene7.com/is/image/academy/20825619"
    print(f"Testing with URL: {test_url}")
    
    image_bytes = analyzer.fetch_image(test_url)
    if image_bytes:
        print(f"Image fetched: {len(image_bytes)} bytes")
        
        if analyzer._client:
            result = analyzer.analyze_image(image_bytes)
            print(f"\nAnalysis:\n{result.get('raw_analysis', 'No analysis')[:500]}...")
        else:
            print("Skipping analysis - no API key set")
    else:
        print("Failed to fetch image")

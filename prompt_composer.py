"""
Prompt Composer for AI Product Imagery Workflow

Composes artistically crafted prompts that embed governance constraints
naturally, using compositional techniques for compliance.
"""

from typing import Optional


class PromptComposer:
    """Composes optimized prompts for product image generation."""
    
    # Base prompt template components
    STYLE_PREFIX = "Professional commercial product photography"
    QUALITY_SUFFIX = "ultra high resolution, photorealistic, studio quality, sharp focus on product"
    
    # Compositional techniques for face avoidance
    FACE_AVOIDANCE_PHRASES = [
        "shot from behind showing back of hands only",
        "over-the-shoulder perspective with subject not visible",
        "hands-only composition",
        "product displayed without human presence",
        "static display presentation",
        "collector's showcase presentation",
    ]
    
    def __init__(self):
        """Initialize prompt composer."""
        pass
    
    def compose_prompt(
        self,
        product: dict,
        visible_features: dict,
        governance: dict,
        scene_template: str,
        variation: int = 1
    ) -> dict:
        """
        Compose an artistically crafted prompt for image generation.
        
        Args:
            product: Product data with name, brand, etc.
            visible_features: Features verified from ghost image analysis
            governance: Compiled governance constraints
            scene_template: Scene description from governance rules
            variation: 1 or 2 for different lifestyle variations
            
        Returns:
            Dict with 'positive_prompt' and 'negative_prompt'
        """
        # Build product description from visible features
        product_desc = self._build_product_description(product, visible_features)
        
        # Select face avoidance strategy
        face_strategy = self._select_face_avoidance(governance, variation)
        
        # Build the main prompt
        positive_prompt = self._construct_positive_prompt(
            product_desc=product_desc,
            scene_template=scene_template,
            face_strategy=face_strategy,
            quality_standards=governance.get('quality_standards', []),
            required_elements=governance.get('required_elements', [])
        )
        
        # Build negative prompt
        negative_prompt = self._construct_negative_prompt(
            governance.get('negative_prompts', [])
        )
        
        return {
            'positive_prompt': positive_prompt,
            'negative_prompt': negative_prompt,
            'product_name': product.get('product_name', 'Product'),
            'variation': variation
        }
    
    def _build_product_description(
        self, 
        product: dict, 
        visible_features: dict
    ) -> str:
        """Build product description using only visible features."""
        parts = []
        
        # Brand and product name
        brand = product.get('brand', '')
        name = product.get('product_name', '')
        
        if brand and brand != 'Unknown':
            parts.append(f"{brand}")
        
        # Extract short product type from name
        if name:
            # Clean up name - take essential parts
            name_parts = name.split(':')[0]  # Remove caliber suffix
            parts.append(name_parts)
        
        # Add visible features
        visible_list = visible_features.get('visible_features', [])
        if visible_list:
            visible_attrs = []
            for feat in visible_list[:5]:  # Limit to 5 most relevant
                attr = feat.get('attribute', '')
                val = feat.get('value', '')
                if attr in ['Finish', 'Grip', 'Frame Material'] and val:
                    visible_attrs.append(str(val).lower())
            
            if visible_attrs:
                parts.append(f"with {', '.join(visible_attrs)}")
        
        return " ".join(parts)
    
    def _select_face_avoidance(self, governance: dict, variation: int) -> str:
        """Select appropriate face avoidance strategy."""
        human_policy = governance.get('human_presence', {})
        allowed = human_policy.get('allowed', 'none')
        
        if allowed == 'none':
            # Static display, no humans at all
            return "product displayed without human presence, static presentation"
        elif allowed == 'hands_only':
            # Hands can appear but no identity
            return human_policy.get('guidance', 
                "hands interacting with product, never above wrist, no distinctive features")
        elif allowed == 'silhouette':
            return "silhouette of person in background, face not visible, backlighting"
        else:
            return "product as primary focus, any human elements compositionally avoiding face"
    
    def _construct_positive_prompt(
        self,
        product_desc: str,
        scene_template: str,
        face_strategy: str,
        quality_standards: list,
        required_elements: list
    ) -> str:
        """Construct the main positive prompt."""
        components = [
            self.STYLE_PREFIX,
            f"of {product_desc}",
            scene_template,
            face_strategy,
        ]
        
        # Add key required elements (max 3 to avoid prompt bloat)
        key_required = [r for r in required_elements if 'product' in r.lower() or 'focus' in r.lower()][:3]
        if key_required:
            components.append(", ".join(key_required))
        
        # Add quality suffix
        components.append(self.QUALITY_SUFFIX)
        
        # Combine with proper formatting
        prompt = ", ".join(components)
        
        # Add aspect ratio hint
        prompt += ", square format 1:1 aspect ratio"
        
        return prompt
    
    def _construct_negative_prompt(self, negative_prompts: list) -> str:
        """Construct negative prompt string."""
        # Standard negatives for quality
        standard_negatives = [
            "blurry",
            "low resolution",
            "watermark",
            "text overlay",
            "logo overlay",
            "artificial looking",
            "CGI render",
            "floating product",
            "incorrect proportions",
            "distorted",
        ]
        
        # Combine governance negatives with standard
        all_negatives = list(set(negative_prompts + standard_negatives))
        
        return ", ".join(all_negatives)
    
    def compose_batch_prompts(
        self,
        product: dict,
        visible_features: dict,
        governance: dict,
        scene_templates: dict
    ) -> list[dict]:
        """
        Compose prompts for both lifestyle variations.
        
        Args:
            product: Product data
            visible_features: Verified features from vision analysis
            governance: Compiled constraints
            scene_templates: Dict with 'lifestyle_1' and 'lifestyle_2' templates
            
        Returns:
            List of 2 prompt dicts
        """
        prompts = []
        
        for variation in [1, 2]:
            template_key = f'lifestyle_{variation}'
            scene_template = scene_templates.get(template_key, '')
            
            prompt = self.compose_prompt(
                product=product,
                visible_features=visible_features,
                governance=governance,
                scene_template=scene_template,
                variation=variation
            )
            prompts.append(prompt)
        
        return prompts


def create_prompt_composer() -> PromptComposer:
    """Factory function to create PromptComposer."""
    return PromptComposer()


if __name__ == "__main__":
    # Test prompt composition
    composer = create_prompt_composer()
    
    # Sample product data
    test_product = {
        'product_name': 'Springfield XDS MOD2 OSP 45ACP 3.3" Pistol',
        'brand': 'Springfield Armory',
        'class_description': 'Handguns - Semi-Auto Centerfire'
    }
    
    test_visible = {
        'visible_features': [
            {'attribute': 'Finish', 'value': 'Black/Grey'},
            {'attribute': 'Grip', 'value': 'Textured / Stippled'},
        ]
    }
    
    test_governance = {
        'negative_prompts': ['finger on trigger', 'human face', 'aggressive stance'],
        'required_elements': ['product as primary focus', 'photorealistic'],
        'quality_standards': ['high resolution', 'professional lighting'],
        'human_presence': {'allowed': 'hands_only', 'guidance': 'hands only, never above wrist'}
    }
    
    test_scene = "elegant display on weathered wooden desk surface, soft natural morning light"
    
    result = composer.compose_prompt(
        product=test_product,
        visible_features=test_visible,
        governance=test_governance,
        scene_template=test_scene,
        variation=1
    )
    
    print("=== POSITIVE PROMPT ===")
    print(result['positive_prompt'])
    print("\n=== NEGATIVE PROMPT ===")
    print(result['negative_prompt'])

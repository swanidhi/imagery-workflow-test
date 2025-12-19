"""
Prompt Composer V2 for Nano Banana Pro Architecture

Enhanced prompt composition with:
- DoP (Director of Photography) language
- Enhanced physics prompting
- Identity Locking instructions
- Hierarchical grounding for unverified features
"""

from typing import Optional


class PromptComposerV2:
    """
    V2 Prompt Composer with enhanced photographic language.
    
    Key differences from V1:
    - Uses DoP language (lens specs, film grain, bokeh)
    - Enhanced physics instructions
    - Explicit Identity Locking block
    - Handles unverified features with explicit exclusion
    """
    
    # Enhanced style prefix with DoP language
    STYLE_PREFIX = "Ultra-high-end commercial product photography, captured with a 100mm f/2.8 macro lens"
    
    # Enhanced quality suffix with photographic specifics
    QUALITY_SUFFIX = """sharp focus on product, shallow depth of field with bokeh background, 
professional studio lighting with softbox key light at 45 degrees, 
subtle fill light, photorealistic rendering, 8K resolution quality, 
slight film grain for authenticity, no plastic or CGI look"""
    
    # Physics-focused language
    PHYSICS_BLOCK = """The product has mass and weight. 
Render realistic contact shadows where the product meets the surface. 
The bottom of the product should interact with the surface texture naturally.
The product must be grounded, not floating. 
Lighting and shadows must be consistent with a single light source."""
    
    # Face avoidance strategies
    FACE_AVOIDANCE_PHRASES = {
        'none': "product displayed without human presence, static presentation",
        'hands_only': "Show only adult hands interacting with product if needed, never above wrist, no jewelry or distinctive features, no fingernails visible",
        'silhouette': "silhouette of adult person in background, face completely hidden, backlighting only"
    }
    
    def __init__(self):
        """Initialize V2 prompt composer."""
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
        Compose an enhanced prompt for V2 image generation.
        
        Returns:
            Dict with 'positive_prompt', 'negative_prompt', 'product_name', 'variation'
        """
        # Build product description from VISIBLE features only
        product_desc = self._build_product_description(product, visible_features)
        
        # Build identity locking instruction for unverified features
        identity_lock = self._build_identity_lock(visible_features)

        # Select face avoidance strategy
        face_strategy = self._select_face_avoidance(governance, variation)
        
        # Handle Smart Context Selection if scene_template is a list/options
        scene_instruction = scene_template
        if isinstance(scene_template, list):
            options_text = "\n".join([f"- {opt}" for opt in scene_template])
            
            # Build product attributes summary for context selection (Nano Banana §6.3)
            visible_attrs = visible_features.get('visible_features', [])
            attr_summary = []
            for feat in visible_attrs[:8]:
                attr = feat.get('attribute', '')
                val = feat.get('value', '')
                if attr and val:
                    attr_summary.append(f"{attr}: {val}")
            
            product_attrs_text = ", ".join(attr_summary) if attr_summary else "standard product"
            product_class = product.get('class_description', '')
            product_brand = product.get('brand', '')
            
            scene_instruction = f"""
CONTEXTUAL REASONING TASK:
Product Attributes: {product_attrs_text}
Product Class: {product_class}
Brand: {product_brand}

Based on these attributes, select the SINGLE most appropriate setting from the following options:
{options_text}

Example reasoning:
- If wood stock/heritage finish → select Heritage/Western context
- If polymer/tactical → select Tactical/Modern context
- If competition-grade → select Range/Sport context

Render the scene using the context that best matches this product's aesthetic and intended use case.
"""

        # Build main prompt
        positive_prompt = self._construct_positive_prompt(
            product_desc=product_desc,
            scene_template=scene_instruction,
            face_strategy=face_strategy,
            identity_lock=identity_lock,
            required_elements=governance.get('required_elements', [])
        )

        
        # Build negative prompt
        negative_prompt = self._construct_negative_prompt(
            governance.get('negative_prompts', []),
            visible_features.get('unverified_features', [])
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
        """Build product description using ONLY visible features."""
        parts = []
        
        brand = product.get('brand', '')
        name = product.get('product_name', '')
        
        if brand and brand != 'Unknown':
            parts.append(brand)
        
        if name:
            name_parts = name.split(':')[0]
            parts.append(name_parts)
        
        # Add visible features with DoP language
        visible_list = visible_features.get('visible_features', [])
        if visible_list:
            visible_attrs = []
            for feat in visible_list[:5]:
                attr = feat.get('attribute', '')
                val = feat.get('value', '')
                if attr in ['Finish', 'Grip', 'Frame Material'] and val:
                    visible_attrs.append(str(val).lower())
            
            if visible_attrs:
                parts.append(f"featuring {', '.join(visible_attrs)} (as visible in reference)")
        
        return " ".join(parts)
    
    def _build_identity_lock(self, visible_features: dict) -> str:
        """Build identity locking instruction for unverified features."""
        unverified = visible_features.get('unverified_features', [])
        
        if not unverified:
            return ""
        
        # Extract attribute names that should NOT be rendered
        unverified_attrs = [f.get('attribute', '') for f in unverified if f.get('attribute')]
        
        if unverified_attrs:
            attrs_str = ", ".join(unverified_attrs[:5])
            return f"IDENTITY LOCK: The following features from product specs are NOT visible in the reference images and MUST NOT be hallucinated: {attrs_str}. Render only what is visible in the provided reference."
        
        return ""
    
    def _select_face_avoidance(self, governance: dict, variation: int) -> str:
        """Select appropriate face avoidance strategy."""
        human_policy = governance.get('human_presence', {})
        allowed = human_policy.get('allowed', 'none')
        
        return self.FACE_AVOIDANCE_PHRASES.get(allowed, self.FACE_AVOIDANCE_PHRASES['none'])
    
    def _construct_positive_prompt(
        self,
        product_desc: str,
        scene_template: str,
        face_strategy: str,
        identity_lock: str,
        required_elements: list
    ) -> str:
        """Construct enhanced positive prompt with DoP language."""
        components = [
            self.STYLE_PREFIX,
            f"of {product_desc}",
            scene_template,
            self.PHYSICS_BLOCK,
            face_strategy,
        ]
        
        # Add identity lock if present
        if identity_lock:
            components.append(identity_lock)
        
        # Add key required elements
        key_required = [r for r in required_elements if 'product' in r.lower() or 'focus' in r.lower()][:3]
        if key_required:
            components.append(", ".join(key_required))
        
        # Add quality suffix
        components.append(self.QUALITY_SUFFIX)
        
        # Combine and add aspect ratio
        prompt = ", ".join(components)
        prompt += ", square format 1:1 aspect ratio"
        
        return prompt
    
    def _construct_negative_prompt(
        self, 
        negative_prompts: list,
        unverified_features: list
    ) -> str:
        """Construct enhanced negative prompt."""
        # Standard negatives for quality
        standard_negatives = [
            "blurry", "low resolution", "watermark", "text overlay", "logo overlay",
            "artificial looking", "CGI render", "floating product", "incorrect proportions",
            "distorted", "plastic looking", "oversaturated", "unnatural lighting"
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
        """Compose prompts for both lifestyle variations."""
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


def create_prompt_composer_v2() -> PromptComposerV2:
    """Factory function to create V2 PromptComposer."""
    return PromptComposerV2()


if __name__ == "__main__":
    # Test V2 prompt composition
    composer = create_prompt_composer_v2()
    
    test_product = {
        'product_name': 'Springfield XDS MOD2 OSP 45ACP 3.3" Pistol',
        'brand': 'Springfield Armory',
        'class_description': 'Handguns - Semi-Auto Centerfire'
    }
    
    test_visible = {
        'visible_features': [
            {'attribute': 'Finish', 'value': 'Black/Grey'},
            {'attribute': 'Grip', 'value': 'Textured / Stippled'},
        ],
        'unverified_features': [
            {'attribute': 'Magazine Capacity', 'value': '7+1'},
            {'attribute': 'Trigger Pull', 'value': '5.5 lbs'},
        ]
    }
    
    test_governance = {
        'negative_prompts': ['finger on trigger', 'human face', 'aggressive stance'],
        'required_elements': ['product as primary focus', 'photorealistic'],
        'human_presence': {'allowed': 'hands_only'}
    }
    
    test_scene = "elegant display on weathered wooden desk surface, soft natural morning light"
    
    result = composer.compose_prompt(
        product=test_product,
        visible_features=test_visible,
        governance=test_governance,
        scene_template=test_scene,
        variation=1
    )
    
    print("=== V2 POSITIVE PROMPT ===")
    print(result['positive_prompt'])
    print("\n=== V2 NEGATIVE PROMPT ===")
    print(result['negative_prompt'])

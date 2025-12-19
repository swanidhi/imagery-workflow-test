"""
Workflow V2 Orchestrator for Nano Banana Pro Architecture

Enhanced workflow with:
- V2 Image Generator (System Instructions)
- V2 Prompt Composer (DoP language, Identity Locking)
- Post-generation safety audit
"""

import os
import yaml
from pathlib import Path
from typing import Optional
from datetime import datetime

# Load .env file if present
def load_dotenv():
    """Load environment variables from .env file."""
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_dotenv()

from data_layer import ProductDataLayer, load_config
from governance import GovernanceEngine
from vision_analysis import VisionAnalyzer
from prompt_composer_v2 import PromptComposerV2
from image_generator_v2 import ImageGeneratorV2
from feedback import FeedbackManager


class ProductImageryWorkflowV2:
    """
    V2 Workflow Orchestrator using Nano Banana Pro architecture.
    
    Key differences from V1:
    - Uses V2 ImageGenerator with System Instructions
    - Uses V2 PromptComposer with DoP language
    - Supports up to 14 reference images
    - Optional post-generation safety audit
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize V2 workflow with configuration."""
        self.config_path = config_path
        self.config = load_config(config_path)
        self.engine_version = "v2_nanobananapro"
        
        self._init_components()
    
    def _init_components(self) -> None:
        """Initialize all V2 workflow components."""
        # Data layer (same as V1)
        self.data = ProductDataLayer(self.config['data']['csv_path'])
        
        # Governance (same as V1)
        self.governance = GovernanceEngine()
        
        # Vision analyzer (same as V1)
        vision_model = self.config.get('models', {}).get('vision_analysis', 'gemini-2.5-flash')
        self.vision = VisionAnalyzer(model_name=vision_model)
        
        # V2 Prompt Composer
        self.composer = PromptComposerV2()
        
        # V2 Image Generator
        v2_config = self.config.get('generation', {}).get('v2', {})
        self.generator = ImageGeneratorV2(
            model_name=self.config.get('models', {}).get('image_generation', 'gemini-3-pro-image-preview'),
            output_base=self.config.get('output', {}).get('base_path', './output'),
            aspect_ratio=v2_config.get('aspect_ratio', '1:1'),
            image_size=v2_config.get('image_size', '1K'),
            counter_start=self.config.get('output', {}).get('counter_start', 101),
            counter_max=self.config.get('output', {}).get('counter_max', 110),
            safety_constitution_path=v2_config.get('system_instruction_file', 'safety_constitution.yaml')
        )
        
        # Feedback manager (same as V1)
        self.feedback = FeedbackManager()
        
        # Post-generation audit setting
        self.post_audit_enabled = v2_config.get('post_generation_audit', False)
    
    def run(
        self, 
        product_id: str, 
        skip_vision: bool = False,
        verbose: bool = False,
        **kwargs
    ) -> dict:
        """
        Run V2 workflow for a single product.
        
        Args:
            product_id: SKU or cupidName
            skip_vision: Skip ghost image analysis
            verbose: Print detailed progress
            
        Returns:
            Result dict with generated image paths and metadata
        """
        result = {
            'product_id': product_id,
            'success': False,
            'images': [],
            'prompts': [],
            'errors': [],
            'engine_version': self.engine_version,
            'timestamp': datetime.now().isoformat()
        }
        
        # Step 1: Lookup product
        if verbose:
            print(f"[V2][1/6] Looking up product: {product_id}")
        
        product = self.data.get_product(product_id)
        if not product:
            result['errors'].append(f"Product not found: {product_id}")
            return result
        
        cupid_name = product.get('cupidName', product_id)
        tranche = product.get('Tranche', 'Unknown')
        class_desc = product.get('Class Description', '')
        
        result['cupid_name'] = cupid_name
        result['tranche'] = tranche
        result['product_name'] = product.get('SKU Main Description', '')
        result['class_description'] = class_desc
        
        if verbose:
            print(f"    Found: {result['product_name']}")
            print(f"    Class: {class_desc}, Tranche: {tranche}")
        
        # Step 2: Get product features and analyze ghost images
        selected_urls = kwargs.get('selected_ghost_urls', [])
        if verbose:
            print(f"[V2][2/6] Analyzing product features (up to 14 images supported)")
        
        features = self.data.get_product_features(product)
        ghost_urls = self.data.get_ghost_image_urls(product)
        
        visible_features = {'visible_features': [], 'unverified_features': []}
        reference_images = []
        
        if ghost_urls and not skip_vision:
            visible_features = self.vision.analyze_ghost_images(
                image_urls=ghost_urls,
                product_specs=features
            )
            
            # V2: Support up to 14 reference images
            urls_to_fetch = selected_urls if (selected_urls and len(selected_urls) > 0) else ghost_urls[:5]
            
            for url in urls_to_fetch[:14]:
                if url in ghost_urls:
                    img_bytes = self.vision.fetch_image(url)
                    if img_bytes:
                        reference_images.append(img_bytes)
            
            if verbose:
                print(f"    Analyzed {len(ghost_urls)} ghost images")
                print(f"    Using {len(reference_images)} images for Identity Locking")
                print(f"    Visible features: {len(visible_features.get('visible_features', []))}")
                print(f"    Unverified features: {len(visible_features.get('unverified_features', []))}")
        
        # Step 3: Compile governance constraints
        if verbose:
            print(f"[V2][3/6] Compiling governance constraints")
        
        feedback_data = self.feedback.get_refinements()
        constraints = self.governance.compile_constraints(class_desc, feedback_data)
        constraints = self._enhance_with_semantic_context(constraints, features)
        
        if verbose:
            print(f"    Negative prompts: {len(constraints['negative_prompts'])}")
        
        # Step 4: Compose V2 prompts
        if verbose:
            print(f"[V2][4/6] Composing prompts (DoP language, Identity Lock)")
        
        scene_templates = {
            'lifestyle_1': self.governance.get_scene_template(class_desc, 1),
            'lifestyle_2': self.governance.get_scene_template(class_desc, 2),
        }
        
        prompts = self.composer.compose_batch_prompts(
            product=features,
            visible_features=visible_features,
            governance=constraints,
            scene_templates=scene_templates
        )
        
        result['prompts'] = prompts
        
        # Step 5: Generate images with V2 generator
        if verbose:
            print(f"[V2][5/6] Generating images (System Instructions enabled)")
        
        # Prepare trace metadata
        trace_metadata = {
            "vision_analysis": {
                "visible_features": visible_features.get('visible_features', []),
                "unverified_features": visible_features.get('unverified_features', []),
                "reference_images_count": len(reference_images)
            },
            "governance": {
                "constraints": constraints,
                "scene_templates": scene_templates
            },
            "product_context": {
                "cupid_name": cupid_name,
                "tranche": tranche,
                "class_description": class_desc
            },
            "engine_version": self.engine_version
        }
        
        for prompt_data in prompts:
            current_metadata = trace_metadata.copy()
            current_metadata['prompt_variation'] = prompt_data
            
            gen_result = self.generator.generate_and_save(
                prompt=prompt_data['positive_prompt'],
                negative_prompt=prompt_data['negative_prompt'],
                tranche=tranche,
                cupid_name=cupid_name,
                reference_images=reference_images,
                metadata=current_metadata
            )
            
            if gen_result['success']:
                result['images'].append(gen_result['path'])
                if verbose:
                    print(f"    ✓ Saved: {gen_result['path']}")
            else:
                result['errors'].append(gen_result.get('error', 'Unknown error'))
                if verbose:
                    print(f"    ✗ Failed: {gen_result.get('error')}")
        
        # Step 6: Post-generation audit (if enabled)
        if self.post_audit_enabled and result['images']:
            if verbose:
                print(f"[V2][6/6] Running post-generation safety audit")
            # TODO: Implement post-generation audit using VisionAnalyzer
            # This would check generated images for safety violations
        else:
            if verbose:
                print(f"[V2][6/6] Post-generation audit: Skipped")
        
        result['success'] = len(result['images']) > 0
        return result
    
    def _enhance_with_semantic_context(
        self, 
        constraints: dict, 
        features: dict
    ) -> dict:
        """Enhance constraints with semantic context (same as V1)."""
        specs = features.get('specifications', {})
        
        visibility_requirements = [
            "product fully visible and unobstructed",
            "product is the hero of the image",
            "product prominently displayed",
            "entire product visible in frame",
        ]
        constraints['required_elements'].extend(visibility_requirements)
        
        constraints['semantic_requirements'] = {
            'product_fully_visible': True,
            'adult_hands_only': True,
            'product_grounded': True,
            'proportions_realistic': True,
        }
        
        return constraints


def create_workflow_v2(config_path: str = "config.yaml") -> ProductImageryWorkflowV2:
    """Factory function to create V2 workflow."""
    return ProductImageryWorkflowV2(config_path)


if __name__ == "__main__":
    import sys
    
    workflow = create_workflow_v2()
    
    print(f"Engine Version: {workflow.engine_version}")
    print(f"Total products: {workflow.data.total_products}")
    print(f"Products with images: {workflow.data.products_with_images}")
    
    if len(sys.argv) > 1:
        product_id = sys.argv[1]
        print(f"\nRunning V2 workflow for: {product_id}")
        result = workflow.run(product_id, verbose=True)
        print(f"\nResult: {result}")

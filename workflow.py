"""
Main Workflow Orchestrator for AI Product Imagery

Coordinates all components to generate lifestyle product images
with governance compliance and semantic validation.
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
from governance import GovernanceEngine, load_feedback
from vision_analysis import VisionAnalyzer
from prompt_composer import PromptComposer
from image_generator import ImageGenerator
from feedback import FeedbackManager


class ProductImageryWorkflow:
    """Main workflow orchestrator for product image generation."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize workflow with configuration.
        
        Args:
            config_path: Path to config.yaml
        """
        self.config_path = config_path
        self.config = load_config(config_path)
        
        # Initialize components
        self._init_components()
    
    def _init_components(self) -> None:
        """Initialize all workflow components."""
        # Data layer
        self.data = ProductDataLayer(self.config['data']['csv_path'])
        
        # Governance
        self.governance = GovernanceEngine()
        
        # Vision analyzer
        vision_model = self.config.get('models', {}).get('vision_analysis', 'gemini-2.5-flash')
        self.vision = VisionAnalyzer(model_name=vision_model)
        
        # Prompt composer
        self.composer = PromptComposer()
        
        # Image generator - uses actual API model IDs from config
        self.generator = ImageGenerator(
            model_name=self.config.get('models', {}).get('image_generation', 'gemini-2.0-flash-exp'),
            output_base=self.config.get('output', {}).get('base_path', './output'),
            counter_start=self.config.get('output', {}).get('counter_start', 101),
            counter_max=self.config.get('output', {}).get('counter_max', 110)
        )
        
        # Feedback manager
        self.feedback = FeedbackManager()
    
    def run(
        self, 
        product_id: str, 
        skip_vision: bool = False,
        verbose: bool = False,
        **kwargs
    ) -> dict:
        """
        Run the complete workflow for a single product.
        
        Args:
            product_id: SKU or cupidName
            skip_vision: Skip ghost image analysis (use product specs only)
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
            'timestamp': datetime.now().isoformat()
        }
        
        # Step 1: Lookup product
        if verbose:
            print(f"[1/5] Looking up product: {product_id}")
        
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
            print(f"    Selected Context Config: {len(selected_urls) if selected_urls else 'Default (First 2)'} images")
            print(f"[2/5] Analyzing product features and ghost images")
        
        features = self.data.get_product_features(product)
        ghost_urls = self.data.get_ghost_image_urls(product)
        
        visible_features = {'visible_features': [], 'unverified_features': []}
        reference_images = []
        
        if ghost_urls and not skip_vision:
            # Analyze all ghost images for robust feature extraction
            visible_features = self.vision.analyze_ghost_images(
                image_urls=ghost_urls,
                product_specs=features
            )
            
            # Fetch reference images for generation context
            if selected_urls and isinstance(selected_urls, list) and len(selected_urls) > 0:
                 if verbose: print(f"    Using {len(selected_urls)} selected images for context.")
                 for url in selected_urls:
                     if url in ghost_urls: # Simple validation
                         img_bytes = self.vision.fetch_image(url)
                         if img_bytes:
                             reference_images.append(img_bytes)
            else:
                # Default behavior: use up to 2
                for url in ghost_urls[:2]:
                    img_bytes = self.vision.fetch_image(url)
                    if img_bytes:
                        reference_images.append(img_bytes)
            
            if verbose:
                print(f"    Analyzed {len(ghost_urls)} ghost images")
                print(f"    Using {len(reference_images)} images as context for generation")
                print(f"    Visible features: {len(visible_features.get('visible_features', []))}")
        else:
            if verbose:
                print(f"    Skipping vision analysis (no images or skip_vision=True)")
        
        # Step 3: Compile governance constraints with semantic context
        if verbose:
            print(f"[3/5] Compiling governance constraints")
        
        feedback_data = self.feedback.get_refinements()
        constraints = self.governance.compile_constraints(class_desc, feedback_data)
        
        # Add semantic context based on product specifications
        constraints = self._enhance_with_semantic_context(constraints, features)
        
        if verbose:
            print(f"    Negative prompts: {len(constraints['negative_prompts'])}")
            print(f"    Required elements: {len(constraints['required_elements'])}")
        
        # Step 4: Compose prompts for both variations
        if verbose:
            print(f"[4/5] Composing prompts")
        
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
        
        if verbose:
            for i, p in enumerate(prompts):
                print(f"    Variation {i+1}: {p['positive_prompt'][:80]}...")
        
        # Step 5: Generate images
        if verbose:
            print(f"[5/5] Generating images")
        
        # Step 5: Generate images
        if verbose:
            print(f"[5/5] Generating images")
        
        # Prepare trace metadata for audit logs
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
            }
        }

        for prompt_data in prompts:
            # Clone metadata for each generation to avoid mutation issues
            current_metadata = trace_metadata.copy()
            current_metadata['prompt_variation'] = prompt_data # Include specific prompt details
            
            gen_result = self.generator.generate_and_save(
                prompt=prompt_data['positive_prompt'],
                negative_prompt=prompt_data['negative_prompt'],
                tranche=tranche,
                cupid_name=cupid_name,
                reference_images=reference_images,
                metadata=current_metadata # Pass full trace
            )
            
            if gen_result['success']:
                result['images'].append(gen_result['path'])
                if verbose:
                    print(f"    ✓ Saved: {gen_result['path']}")
            else:
                result['errors'].append(gen_result.get('error', 'Unknown error'))
                if verbose:
                    print(f"    ✗ Failed: {gen_result.get('error')}")
        
        result['success'] = len(result['images']) > 0
        return result
    
    def _enhance_with_semantic_context(
        self, 
        constraints: dict, 
        features: dict
    ) -> dict:
        """
        Enhance constraints with semantic context from product specifications.
        
        CRITICAL: Product must ALWAYS be fully visible and prominent.
        Context describes the SCENE AROUND the product, never hides it.
        """
        specs = features.get('specifications', {})
        enrichment = features.get('enrichment', {})
        
        # ALWAYS require product visibility - this is non-negotiable for e-commerce
        visibility_requirements = [
            "product fully visible and unobstructed",
            "product is the hero of the image",
            "product prominently displayed",
            "entire product visible in frame",
            "no part of product hidden or concealed",
        ]
        constraints['required_elements'].extend(visibility_requirements)
        
        # Determine SCENE context (what's AROUND the visible product)
        product_type = specs.get('Product Type', '').lower()
        handgun_size = specs.get('Handgun Size', '').lower()
        
        scene_context = []
        
        # Size informs the SCENE backdrop, not product placement
        if 'compact' in handgun_size or 'sub compact' in handgun_size:
            # Compact guns: personal/home scenes with product ON DISPLAY
            scene_context.append("personal desk or nightstand setting")
        elif 'full' in handgun_size:
            # Full size: range or professional settings
            scene_context.append("shooting range bench or armory setting")
        
        # Type informs environmental backdrop
        if 'shotgun' in product_type:
            scene_context.append("outdoor sporting environment backdrop")
        elif 'rifle' in product_type:
            scene_context.append("hunting lodge or precision range setting")
        
        # These describe SCENE, not product state
        constraints['scene_context'] = scene_context
        
        # Semantic validation requirements
        constraints['semantic_requirements'] = {
            'product_fully_visible': True,  # CRITICAL
            'adult_hands_only': True,
            'product_grounded': True,  # Not floating
            'proportions_realistic': True,
            'no_product_concealment': True,  # Never hide in holster/case
        }
        
        return constraints
    
    def batch_run(
        self,
        product_ids: list[str],
        verbose: bool = False,
        stop_on_error: bool = False
    ) -> dict:
        """
        Run workflow for multiple products.
        
        Args:
            product_ids: List of SKUs or cupidNames
            verbose: Print progress
            stop_on_error: Stop if any product fails
            
        Returns:
            Batch result with summary and individual results
        """
        batch_result = {
            'total': len(product_ids),
            'success': 0,
            'failed': 0,
            'results': [],
            'timestamp': datetime.now().isoformat()
        }
        
        for i, product_id in enumerate(product_ids):
            if verbose:
                print(f"\n{'='*60}")
                print(f"Processing {i+1}/{len(product_ids)}: {product_id}")
                print('='*60)
            
            result = self.run(product_id, verbose=verbose)
            batch_result['results'].append(result)
            
            if result['success']:
                batch_result['success'] += 1
            else:
                batch_result['failed'] += 1
                if stop_on_error:
                    if verbose:
                        print(f"Stopping due to error: {result['errors']}")
                    break
        
        return batch_result
    
    def run_by_tranche(
        self,
        tranche: str,
        limit: Optional[int] = None,
        verbose: bool = False
    ) -> dict:
        """Run workflow for all products in a tranche."""
        products = self.data.get_products_by_tranche(tranche, limit=limit)
        product_ids = [p['cupidName'] for p in products if p.get('cupidName')]
        
        if verbose:
            print(f"Found {len(product_ids)} products in {tranche}")
        
        return self.batch_run(product_ids, verbose=verbose)
    
    def run_by_class(
        self,
        class_description: str,
        limit: Optional[int] = None,
        verbose: bool = False
    ) -> dict:
        """Run workflow for all products in a class."""
        products = self.data.get_products_by_class(class_description, limit=limit)
        product_ids = [p['cupidName'] for p in products if p.get('cupidName')]
        
        if verbose:
            print(f"Found {len(product_ids)} products in {class_description}")
        
        return self.batch_run(product_ids, verbose=verbose)


def create_workflow(config_path: str = "config.yaml") -> ProductImageryWorkflow:
    """Factory function to create workflow."""
    return ProductImageryWorkflow(config_path)


if __name__ == "__main__":
    # Quick test
    import sys
    
    workflow = create_workflow()
    
    print(f"Total products: {workflow.data.total_products}")
    print(f"Products with images: {workflow.data.products_with_images}")
    
    # If a product ID is provided, run for that product
    if len(sys.argv) > 1:
        product_id = sys.argv[1]
        print(f"\nRunning workflow for: {product_id}")
        result = workflow.run(product_id, verbose=True)
        print(f"\nResult: {result}")

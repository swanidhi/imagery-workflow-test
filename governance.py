"""
Governance Rules Engine for AI Product Imagery Workflow

Loads and applies governance rules based on product class.
"""

import yaml
from pathlib import Path
from typing import Optional


class GovernanceEngine:
    """Manages governance rules for product imagery."""
    
    def __init__(self, rules_path: str = "governance_rules.yaml"):
        """Initialize with governance rules file."""
        self.rules_path = Path(rules_path)
        self._rules: dict = {}
        self._load_rules()
    
    def _load_rules(self) -> None:
        """Load governance rules from YAML."""
        if not self.rules_path.exists():
            raise FileNotFoundError(f"Governance rules not found: {self.rules_path}")
        
        with open(self.rules_path, 'r') as f:
            self._rules = yaml.safe_load(f)
    
    def get_universal_rules(self) -> dict:
        """Get universal rules that apply to all products."""
        return self._rules.get('universal', {})
    
    def get_scene_category(self, class_description: str) -> tuple[str, bool]:
        """
        Map class description to scene category.
        
        Returns:
            Tuple of (category, is_missing) - is_missing=True if class not found in mapping
        """
        mapping = self._rules.get('class_mapping', {})
        if class_description in mapping:
            return mapping[class_description], False
        else:
            # Return default but flag as missing
            return 'handguns', True
    
    def get_scene_template(self, class_description: str, variation: int) -> str:
        """
        Get scene template for a product class and variation.
        
        Args:
            class_description: Product class (e.g., "Handguns - Semi-Auto Centerfire")
            variation: 1 or 2 for different lifestyle scenes
            
        Returns:
            Scene template string
        """
        category, _ = self.get_scene_category(class_description)
        templates = self._rules.get('scene_templates', {}).get(category, {})
        
        # New Schema: 'options' list
        options = templates.get('options', [])
        
        if not options:
            # Fallback to old schema if needed
            template_key = f'lifestyle_{variation}'
            return templates.get(template_key, '')

        # Return ALL options if requested (special variation 999 or just handling list upstream)
        # But for backward compatibility with calls expecting a string, we return a random choice 
        # UNLESS the caller asked for the list (which we haven't implemented a separate method for yet)
        # Let's create a get_scene_options method instead and keep this for random fallback.
        import random
        return random.choice(options)

    def get_scene_options(self, class_description: str) -> tuple[list[str], bool]:
        """
        Get all available scene options for a class.
        
        Returns:
            Tuple of (options_list, is_class_missing)
        """
        category, is_missing = self.get_scene_category(class_description)
        templates = self._rules.get('scene_templates', {}).get(category, {})
        return templates.get('options', []), is_missing
    
    def get_class_overrides(self, class_description: str) -> dict:
        """Get class-specific rule overrides."""
        overrides = self._rules.get('class_overrides', {})
        return overrides.get(class_description, {})
    
    def compile_constraints(
        self, 
        class_description: str, 
        feedback: Optional[dict] = None
    ) -> dict:
        """
        Compile all applicable constraints for a product class.
        
        Args:
            class_description: Product class
            feedback: Optional feedback dict for refinements
            
        Returns:
            Complete constraints dict with negative_prompts, required_elements, etc.
        """
        universal = self.get_universal_rules()
        overrides = self.get_class_overrides(class_description)
        
        # Start with universal rules
        constraints = {
            'negative_prompts': list(universal.get('negative_prompts', [])),
            'required_elements': list(universal.get('required_elements', [])),
            'face_policy': universal.get('face_policy', 'avoid_compositionally'),
            'human_presence': universal.get('human_presence', {}),
            'quality_standards': list(self._rules.get('quality_standards', [])),
        }
        
        # Apply class-specific overrides
        if overrides:
            # Add additional negative prompts
            additional_negatives = overrides.get('additional_negative_prompts', [])
            constraints['negative_prompts'].extend(additional_negatives)
            
            # Add additional required elements
            additional_required = overrides.get('additional_required_elements', [])
            constraints['required_elements'].extend(additional_required)
            
            # Add preferred elements
            preferred = overrides.get('preferred_elements', [])
            constraints['required_elements'].extend(preferred)
        
        # Apply feedback refinements if available
        if feedback:
            self._apply_feedback_refinements(constraints, class_description, feedback)
        
        return constraints
    
    def _apply_feedback_refinements(
        self, 
        constraints: dict, 
        class_description: str,
        feedback: dict
    ) -> None:
        """Apply feedback-based refinements to constraints."""
        refinements = feedback.get('rule_refinements', {})
        category = self.get_scene_category(class_description)
        
        category_refinements = refinements.get(category, {})
        
        # Add to required elements
        add_to_required = category_refinements.get('add_to_required', [])
        constraints['required_elements'].extend(add_to_required)
        
        # Add to negative prompts
        add_to_negative = category_refinements.get('add_to_negative', [])
        constraints['negative_prompts'].extend(add_to_negative)
    
    def format_negative_prompt(self, constraints: dict) -> str:
        """Format negative prompts for image generation API."""
        negatives = constraints.get('negative_prompts', [])
        return ", ".join(negatives)
    
    def format_quality_requirements(self, constraints: dict) -> str:
        """Format quality requirements as prompt text."""
        quality = constraints.get('quality_standards', [])
        required = constraints.get('required_elements', [])
        return ", ".join(quality + required)


def load_feedback(feedback_path: str = "feedback.yaml") -> dict:
    """Load feedback file."""
    path = Path(feedback_path)
    if not path.exists():
        return {'feedback_entries': {}, 'rule_refinements': {}}
    
    with open(path, 'r') as f:
        return yaml.safe_load(f) or {'feedback_entries': {}, 'rule_refinements': {}}


def create_governance_engine(rules_path: str = "governance_rules.yaml") -> GovernanceEngine:
    """Factory function to create GovernanceEngine."""
    return GovernanceEngine(rules_path)


if __name__ == "__main__":
    # Quick test
    engine = create_governance_engine()
    
    test_classes = [
        "Handguns - Semi-Auto Centerfire",
        "Rifles - Center Fire",
        "Shotguns - Manual",
        "Modern Sporting Rifles",
    ]
    
    for class_desc in test_classes:
        print(f"\n=== {class_desc} ===")
        constraints = engine.compile_constraints(class_desc)
        print(f"Negative prompts: {len(constraints['negative_prompts'])}")
        print(f"Required elements: {len(constraints['required_elements'])}")
        print(f"Scene 1: {engine.get_scene_template(class_desc, 1)[:60]}...")
        print(f"Scene 2: {engine.get_scene_template(class_desc, 2)[:60]}...")

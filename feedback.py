"""
Feedback Management for AI Product Imagery Workflow

Handles loading, saving, and aggregating user feedback.
"""

import yaml
from pathlib import Path
from typing import Optional
from datetime import datetime
from collections import defaultdict


class FeedbackManager:
    """Manages feedback for generated images."""
    
    def __init__(self, feedback_path: str = "feedback.yaml"):
        """Initialize feedback manager."""
        self.feedback_path = Path(feedback_path)
        self._feedback: dict = {}
        self._load_feedback()
    
    def _load_feedback(self) -> None:
        """Load feedback from YAML file."""
        if self.feedback_path.exists():
            with open(self.feedback_path, 'r') as f:
                self._feedback = yaml.safe_load(f) or {}
        else:
            self._feedback = {
                'feedback_entries': {},
                'rule_refinements': {}
            }
    
    def _save_feedback(self) -> None:
        """Save feedback to YAML file."""
        with open(self.feedback_path, 'w') as f:
            yaml.dump(self._feedback, f, default_flow_style=False, sort_keys=False)
    
    def add_feedback(
        self,
        cupid_name: str,
        rating: int,
        issues: Optional[list[str]] = None,
        suggestions: Optional[list[str]] = None,
        regenerate: bool = False,
        approved: bool = False
    ) -> None:
        """
        Add or update feedback for a product.
        
        Args:
            cupid_name: Product identifier
            rating: 1-5 rating
            issues: List of issues observed
            suggestions: List of improvement suggestions
            regenerate: Whether to regenerate images
            approved: Whether images are approved
        """
        if 'feedback_entries' not in self._feedback:
            self._feedback['feedback_entries'] = {}
        
        entry = {
            'rating': max(1, min(5, rating)),
            'timestamp': datetime.now().isoformat(),
        }
        
        if issues:
            entry['issues'] = issues
        if suggestions:
            entry['suggestions'] = suggestions
        if regenerate:
            entry['regenerate'] = True
        if approved:
            entry['approved'] = True
        
        self._feedback['feedback_entries'][cupid_name] = entry
        self._save_feedback()
    
    def get_feedback(self, cupid_name: str) -> Optional[dict]:
        """Get feedback for a specific product."""
        return self._feedback.get('feedback_entries', {}).get(cupid_name)
    
    def get_products_to_regenerate(self) -> list[str]:
        """Get list of products marked for regeneration."""
        entries = self._feedback.get('feedback_entries', {})
        return [
            cupid for cupid, data in entries.items()
            if data.get('regenerate', False) and not data.get('approved', False)
        ]
    
    def mark_regenerated(self, cupid_name: str) -> None:
        """Mark a product as regenerated (clear regenerate flag)."""
        entries = self._feedback.get('feedback_entries', {})
        if cupid_name in entries:
            entries[cupid_name]['regenerate'] = False
            entries[cupid_name]['regenerated_at'] = datetime.now().isoformat()
            self._save_feedback()
    
    def aggregate_learnings(self, class_mapping: dict) -> dict:
        """
        Aggregate feedback into rule refinements by category.
        
        Args:
            class_mapping: Dict mapping class description to category
            
        Returns:
            Aggregated refinements by category
        """
        entries = self._feedback.get('feedback_entries', {})
        
        # Collect issues and suggestions by implied category
        category_issues = defaultdict(list)
        category_suggestions = defaultdict(list)
        
        for cupid_name, data in entries.items():
            # Would need product data to get class - for now aggregate globally
            issues = data.get('issues', [])
            suggestions = data.get('suggestions', [])
            
            category_issues['global'].extend(issues)
            category_suggestions['global'].extend(suggestions)
        
        # Convert to refinements
        refinements = {}
        
        for category in set(list(category_issues.keys()) + list(category_suggestions.keys())):
            issues = category_issues.get(category, [])
            suggestions = category_suggestions.get(category, [])
            
            if issues or suggestions:
                refinements[category] = {}
                
                # Common issue patterns -> negative prompts
                if issues:
                    refinements[category]['common_issues'] = list(set(issues))
                
                # Suggestions -> required elements
                if suggestions:
                    refinements[category]['suggested_improvements'] = list(set(suggestions))
        
        # Update stored refinements
        self._feedback['rule_refinements'] = refinements
        self._save_feedback()
        
        return refinements
    
    def get_refinements(self) -> dict:
        """Get current rule refinements."""
        return self._feedback.get('rule_refinements', {})
    
    def get_stats(self) -> dict:
        """Get feedback statistics."""
        entries = self._feedback.get('feedback_entries', {})
        
        if not entries:
            return {
                'total': 0,
                'approved': 0,
                'pending_regenerate': 0,
                'avg_rating': 0
            }
        
        ratings = [e.get('rating', 3) for e in entries.values()]
        
        return {
            'total': len(entries),
            'approved': sum(1 for e in entries.values() if e.get('approved')),
            'pending_regenerate': sum(1 for e in entries.values() if e.get('regenerate') and not e.get('approved')),
            'avg_rating': sum(ratings) / len(ratings) if ratings else 0
        }


def create_feedback_manager(feedback_path: str = "feedback.yaml") -> FeedbackManager:
    """Factory function to create FeedbackManager."""
    return FeedbackManager(feedback_path)


if __name__ == "__main__":
    # Quick test
    manager = create_feedback_manager()
    
    print("=== Feedback Stats ===")
    stats = manager.get_stats()
    for key, val in stats.items():
        print(f"  {key}: {val}")
    
    print("\n=== Products to Regenerate ===")
    to_regen = manager.get_products_to_regenerate()
    print(f"  {len(to_regen)} products")

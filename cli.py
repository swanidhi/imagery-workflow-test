#!/usr/bin/env python3
"""
CLI Interface for AI Product Imagery Workflow

Command-line interface for generating, reviewing, and managing
AI-generated product imagery.
"""

import argparse
import sys
import os
from pathlib import Path


def ensure_dependencies():
    """Check for required dependencies."""
    missing = []
    try:
        import pandas
    except ImportError:
        missing.append('pandas')
    try:
        import yaml
    except ImportError:
        missing.append('pyyaml')
    try:
        from google import genai
    except ImportError:
        missing.append('google-genai')
    
    if missing:
        print("Missing dependencies. Install with:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)


def cmd_generate(args):
    """Generate images for product(s)."""
    from workflow import create_workflow
    
    workflow = create_workflow(args.config)
    
    if args.id:
        # Single product
        print(f"Generating images for: {args.id}")
        result = workflow.run(
            product_id=args.id,
            skip_vision=args.skip_vision,
            verbose=args.verbose
        )
        
        if result['success']:
            print(f"\n✓ Generated {len(result['images'])} images:")
            for path in result['images']:
                print(f"  - {path}")
        else:
            print(f"\n✗ Failed: {result['errors']}")
        
        return 0 if result['success'] else 1
    
    elif args.tranche:
        # By tranche
        result = workflow.run_by_tranche(
            tranche=args.tranche,
            limit=args.limit,
            verbose=args.verbose
        )
        print(f"\nBatch complete: {result['success']} succeeded, {result['failed']} failed")
        return 0 if result['failed'] == 0 else 1
    
    elif args.class_name:
        # By class
        result = workflow.run_by_class(
            class_description=args.class_name,
            limit=args.limit,
            verbose=args.verbose
        )
        print(f"\nBatch complete: {result['success']} succeeded, {result['failed']} failed")
        return 0 if result['failed'] == 0 else 1
    
    else:
        print("Error: Must specify --id, --tranche, or --class")
        return 1


def cmd_feedback(args):
    """Add feedback for a product."""
    from feedback import create_feedback_manager
    
    manager = create_feedback_manager()
    
    issues = args.issues.split('|') if args.issues else None
    suggestions = args.suggestions.split('|') if args.suggestions else None
    
    manager.add_feedback(
        cupid_name=args.id,
        rating=args.rating,
        issues=issues,
        suggestions=suggestions,
        regenerate=args.regenerate,
        approved=args.approve
    )
    
    print(f"Feedback recorded for: {args.id}")
    print(f"  Rating: {args.rating}/5")
    if issues:
        print(f"  Issues: {issues}")
    if suggestions:
        print(f"  Suggestions: {suggestions}")
    if args.regenerate:
        print(f"  Marked for regeneration")
    if args.approve:
        print(f"  Approved")
    
    return 0


def cmd_regenerate(args):
    """Regenerate images based on feedback."""
    from workflow import create_workflow
    from feedback import create_feedback_manager
    
    workflow = create_workflow(args.config)
    manager = create_feedback_manager()
    
    if args.id:
        product_ids = [args.id]
    else:
        product_ids = manager.get_products_to_regenerate()
    
    if not product_ids:
        print("No products to regenerate")
        return 0
    
    print(f"Regenerating {len(product_ids)} products...")
    
    result = workflow.batch_run(product_ids, verbose=args.verbose)
    
    # Mark as regenerated
    for cupid_name in product_ids:
        manager.mark_regenerated(cupid_name)
    
    print(f"\nRegeneration complete: {result['success']} succeeded, {result['failed']} failed")
    return 0 if result['failed'] == 0 else 1


def cmd_validate_rules(args):
    """Validate governance rules and show sample prompts."""
    from governance import create_governance_engine
    from prompt_composer import create_prompt_composer
    from data_layer import create_data_layer
    import random
    
    engine = create_governance_engine()
    composer = create_prompt_composer()
    data = create_data_layer(args.config)
    
    # Get unique classes
    products = data.get_all_products()
    classes = set(p.get('Class Description') for p in products if p.get('Class Description'))
    
    print(f"Validating rules for {len(classes)} product classes\n")
    
    for class_desc in sorted(classes):
        print(f"\n{'='*60}")
        print(f"CLASS: {class_desc}")
        print('='*60)
        
        constraints = engine.compile_constraints(class_desc)
        
        print(f"\nNegative prompts ({len(constraints['negative_prompts'])}):")
        for neg in constraints['negative_prompts'][:5]:
            print(f"  - {neg}")
        if len(constraints['negative_prompts']) > 5:
            print(f"  ... and {len(constraints['negative_prompts']) - 5} more")
        
        print(f"\nScene templates:")
        print(f"  1: {engine.get_scene_template(class_desc, 1)[:60]}...")
        print(f"  2: {engine.get_scene_template(class_desc, 2)[:60]}...")
        
        # Generate sample prompt
        class_products = [p for p in products if p.get('Class Description') == class_desc]
        if class_products:
            sample = random.choice(class_products)
            sample_features = data.get_product_features(sample)
            
            prompt = composer.compose_prompt(
                product=sample_features,
                visible_features={'visible_features': []},
                governance=constraints,
                scene_template=engine.get_scene_template(class_desc, 1),
                variation=1
            )
            
            print(f"\nSample prompt for {sample.get('cupidName', 'unknown')}:")
            print(f"  {prompt['positive_prompt'][:200]}...")
    
    return 0


def cmd_stats(args):
    """Show workflow statistics."""
    from data_layer import create_data_layer
    from feedback import create_feedback_manager
    
    data = create_data_layer(args.config)
    feedback = create_feedback_manager()
    
    print("=== Product Data ===")
    print(f"Total products: {data.total_products}")
    print(f"Products with ghost images: {data.products_with_images}")
    print(f"Missing ghost images: {data.total_products - data.products_with_images}")
    
    # Tranche breakdown
    products = data.get_all_products()
    tranches = {}
    classes = {}
    
    for p in products:
        tranche = p.get('Tranche', 'Unknown')
        tranches[tranche] = tranches.get(tranche, 0) + 1
        
        class_desc = p.get('Class Description', 'Unknown')
        classes[class_desc] = classes.get(class_desc, 0) + 1
    
    print("\n=== By Tranche ===")
    for t, count in sorted(tranches.items()):
        print(f"  {t}: {count}")
    
    print("\n=== By Class ===")
    for c, count in sorted(classes.items(), key=lambda x: -x[1]):
        print(f"  {c}: {count}")
    
    print("\n=== Feedback ===")
    stats = feedback.get_stats()
    print(f"Total feedback entries: {stats['total']}")
    print(f"Approved: {stats['approved']}")
    print(f"Pending regeneration: {stats['pending_regenerate']}")
    print(f"Average rating: {stats['avg_rating']:.1f}/5")
    
    # Count generated images
    output_path = Path(args.output)
    if output_path.exists():
        image_count = len(list(output_path.rglob("*.jpg")))
        print(f"\n=== Generated Images ===")
        print(f"Total images: {image_count}")
        for tranche_dir in sorted(output_path.iterdir()):
            if tranche_dir.is_dir():
                count = len(list(tranche_dir.glob("*.jpg")))
                print(f"  {tranche_dir.name}: {count}")
    
    return 0


def cmd_list_products(args):
    """List products with optional filtering."""
    from data_layer import create_data_layer
    
    data = create_data_layer(args.config)
    
    if args.tranche:
        products = data.get_products_by_tranche(args.tranche, limit=args.limit)
    elif args.class_name:
        products = data.get_products_by_class(args.class_name, limit=args.limit)
    else:
        products = data.get_all_products(limit=args.limit or 20)
    
    print(f"Showing {len(products)} products:\n")
    
    for p in products:
        cupid = p.get('cupidName', 'N/A')
        name = p.get('SKU Main Description', 'N/A')[:50]
        class_desc = p.get('Class Description', 'N/A')
        tranche = p.get('Tranche', 'N/A')
        images = len(str(p.get('assetDetails', ''))) > 5
        
        print(f"{cupid}")
        print(f"  Name: {name}...")
        print(f"  Class: {class_desc}")
        print(f"  Tranche: {tranche}")
        print(f"  Has images: {'Yes' if images else 'No'}")
        print()
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="AI Product Imagery Workflow CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--config', default='config.yaml', help='Path to config.yaml')
    parser.add_argument('--output', default='./output', help='Output directory')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate product images')
    gen_parser.add_argument('--id', help='Product cupidName or SKU')
    gen_parser.add_argument('--tranche', help='Process all products in tranche')
    gen_parser.add_argument('--class', dest='class_name', help='Process all products in class')
    gen_parser.add_argument('--limit', type=int, help='Limit number of products')
    gen_parser.add_argument('--model', help='Override image generation model')
    gen_parser.add_argument('--skip-vision', action='store_true', help='Skip ghost image analysis')
    gen_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    # Feedback command
    fb_parser = subparsers.add_parser('feedback', help='Add feedback for product')
    fb_parser.add_argument('--id', required=True, help='Product cupidName')
    fb_parser.add_argument('--rating', type=int, required=True, help='Rating 1-5')
    fb_parser.add_argument('--issues', help='Issues (pipe-separated)')
    fb_parser.add_argument('--suggestions', help='Suggestions (pipe-separated)')
    fb_parser.add_argument('--regenerate', action='store_true', help='Mark for regeneration')
    fb_parser.add_argument('--approve', action='store_true', help='Approve images')
    
    # Regenerate command
    regen_parser = subparsers.add_parser('regenerate', help='Regenerate from feedback')
    regen_parser.add_argument('--id', help='Specific product (or all from feedback)')
    regen_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    # Validate command
    val_parser = subparsers.add_parser('validate-rules', help='Validate governance rules')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List products')
    list_parser.add_argument('--tranche', help='Filter by tranche')
    list_parser.add_argument('--class', dest='class_name', help='Filter by class')
    list_parser.add_argument('--limit', type=int, default=20, help='Max products to show')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Check dependencies
    ensure_dependencies()
    
    # Execute command
    commands = {
        'generate': cmd_generate,
        'feedback': cmd_feedback,
        'regenerate': cmd_regenerate,
        'validate-rules': cmd_validate_rules,
        'stats': cmd_stats,
        'list': cmd_list_products,
    }
    
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())

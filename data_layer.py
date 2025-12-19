"""
Data Layer for AI Product Imagery Workflow

Handles CSV loading, product lookup, and data extraction.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Optional
import yaml


class ProductDataLayer:
    """Manages product data access from CSV."""
    
    def __init__(self, csv_path: str):
        """Initialize with CSV file path."""
        self.csv_path = Path(csv_path)
        self._df: Optional[pd.DataFrame] = None
        self._load_data()
    
    def _load_data(self) -> None:
        """Load and cache the CSV data."""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        
        self._df = pd.read_csv(self.csv_path)
        
        # cupidName is unique, use as primary index
        self._by_cupid = {}
        for _, row in self._df.iterrows():
            cupid_name = row.get('cupidName')
            if cupid_name and not pd.isna(cupid_name):
                self._by_cupid[str(cupid_name)] = row.to_dict()
        
        # SKU may have duplicates, store first occurrence only
        self._by_sku = {}
        for _, row in self._df.iterrows():
            sku = row.get('SKU')
            if sku and not pd.isna(sku):
                sku_key = str(int(sku)) if isinstance(sku, float) else str(sku)
                if sku_key not in self._by_sku:
                    self._by_sku[sku_key] = row.to_dict()
    
    def get_product(self, identifier: str) -> Optional[dict]:
        """
        Get product by SKU or cupidName.
        
        Args:
            identifier: Either SKU number or cupidName
            
        Returns:
            Product dict or None if not found
        """
        # Try cupidName first (most common use case)
        if identifier in self._by_cupid:
            return self._by_cupid[identifier]
        
        # Try SKU (convert to int if needed)
        try:
            sku_int = int(identifier)
            if sku_int in self._by_sku:
                return self._by_sku[sku_int]
        except (ValueError, TypeError):
            pass
        
        # Try string SKU
        if identifier in self._by_sku:
            return self._by_sku[identifier]
        
        return None
    
    def get_ghost_image_urls(self, product: dict) -> list[str]:
        """
        Extract ghost image URLs from product's assetDetails.
        
        Args:
            product: Product dictionary
            
        Returns:
            List of Scene7 image URLs
        """
        asset_details = product.get('assetDetails')
        
        if pd.isna(asset_details) or not asset_details:
            return []
        
        try:
            # Parse JSON string
            assets = json.loads(str(asset_details).replace("'", '"'))
            
            # Sort by assetSequence and extract URLs
            sorted_assets = sorted(assets, key=lambda x: int(x.get('assetSequence', 999)))
            return [a.get('imageAddress', '') for a in sorted_assets if a.get('imageAddress')]
        
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Warning: Could not parse assetDetails: {e}")
            return []
    
    def get_product_features(self, product: dict) -> dict:
        """
        Extract enrichment and specification features.
        
        Args:
            product: Product dictionary
            
        Returns:
            Combined features dict with 'enrichment' and 'specifications' keys
        """
        result = {
            'enrichment': {},
            'specifications': {},
            'product_name': product.get('SKU Main Description', ''),
            'brand': product.get('Brand Description', ''),
            'class_description': product.get('Class Description', ''),
            'tranche': product.get('Tranche', ''),
        }
        
        # Parse Enrichment JSON
        enrichment = product.get('Enrichment')
        if not pd.isna(enrichment) and enrichment:
            try:
                result['enrichment'] = json.loads(str(enrichment).replace("'", '"'))
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Parse Specifications JSON
        specifications = product.get('Specifications')
        if not pd.isna(specifications) and specifications:
            try:
                result['specifications'] = json.loads(str(specifications).replace("'", '"'))
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Prioritize Enriched Product Name
        if result['enrichment'] and 'Product Name' in result['enrichment']:
             result['product_name'] = result['enrichment']['Product Name']
        
        return result
    
    def get_products_by_tranche(self, tranche: str, limit: Optional[int] = None) -> list[dict]:
        """Get all products for a specific tranche."""
        filtered = self._df[self._df['Tranche'] == tranche]
        if limit:
            filtered = filtered.head(limit)
        return filtered.to_dict('records')
    
    def get_products_by_class(self, class_description: str, limit: Optional[int] = None) -> list[dict]:
        """Get all products for a specific class description."""
        filtered = self._df[self._df['Class Description'] == class_description]
        if limit:
            filtered = filtered.head(limit)
        return filtered.to_dict('records')
    
    def get_all_products(self, limit: Optional[int] = None) -> list[dict]:
        """Get all products, optionally limited."""
        if limit:
            return self._df.head(limit).to_dict('records')
        return self._df.to_dict('records')
    
    @property
    def total_products(self) -> int:
        """Total number of products in the dataset."""
        return len(self._df)
    
    @property
    def products_with_images(self) -> int:
        """Number of products with ghost images."""
        return self._df['assetDetails'].notna().sum()


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def create_data_layer(config_path: str = "config.yaml") -> ProductDataLayer:
    """Factory function to create ProductDataLayer from config."""
    config = load_config(config_path)
    csv_path = config['data']['csv_path']
    return ProductDataLayer(csv_path)


if __name__ == "__main__":
    # Quick test
    data = create_data_layer()
    print(f"Total products: {data.total_products}")
    print(f"Products with images: {data.products_with_images}")
    
    # Test lookup
    sample_product = data.get_product("133162986_0_0_0_0")
    if sample_product:
        print(f"\nSample product: {sample_product.get('SKU Main Description')}")
        print(f"Ghost images: {len(data.get_ghost_image_urls(sample_product))}")
        features = data.get_product_features(sample_product)
        print(f"Brand: {features['brand']}")
        print(f"Class: {features['class_description']}")

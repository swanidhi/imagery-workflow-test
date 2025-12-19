"""
Review UI Server for AI Product Imagery Workflow (React Backend)

Serves the Vue/React frontend and provides API endpoints.
"""

import json
import os
import yaml
import threading
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

# Load .env
env_path = Path(".env")
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

from data_layer import create_data_layer
from workflow import create_workflow
from workflow_v2 import create_workflow_v2

# Load config to determine engine
def load_config():
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}

config = load_config()
ENGINE_VERSION = config.get('generation', {}).get('engine', 'v1')

# Configure Flask to serve the React build
# 'frontend/dist' contains index.html and assets/
app = Flask(__name__, static_folder='frontend/dist')
CORS(app) # Enable CORS for dev server flexibility

data_layer = None

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/assets/<path:path>')
def serve_assets(path):
    return send_from_directory(os.path.join(app.static_folder, 'assets'), path)

# --- API Endpoints ---

@app.route('/api/products')
def get_products():
    """Get list of ALL products, marking those that have images."""
    global data_layer
    if not data_layer:
        data_layer = create_data_layer()

    generated_cupids = set()
    logs_dir = Path('./output/logs')
    if logs_dir.exists():
        for json_file in logs_dir.rglob('*.json'):
            name_part = json_file.stem
            if '_l1' in name_part:
                 cupid = name_part.rsplit('_', 1)[0]
                 generated_cupids.add(cupid)

    products = []
    products = []
    for cupid, row in data_layer._by_cupid.items():
        products.append({
            'cupid_name': str(cupid),
            'name': str(row.get('SKU Main Description', 'Unknown')),
            'tranche': str(row.get('Tranche', 'Unknown')),
            'class_description': str(row.get('Class Description', '')),
            'has_images': str(cupid) in generated_cupids
        })
    
    products.sort(key=lambda x: (not x['has_images'], x['name']))
    return jsonify({'products': products})

@app.route('/api/product/<cupid_name>')
def get_product(cupid_name):
    global data_layer
    if not data_layer:
        data_layer = create_data_layer()
        
    product = data_layer.get_product(cupid_name)
    if not product:
        return jsonify({'error': 'Not found'}), 404
        
    features = data_layer.get_product_features(product)
    ghost_urls = data_layer.get_ghost_image_urls(product)
    
    generated_images = []
    logs_dir = Path('./output/logs')
    
    if logs_dir.exists():
        for log_file in logs_dir.rglob(f"{cupid_name}_*.json"):
            try:
                with open(log_file) as f:
                    meta = json.load(f)
                tranche = meta.get('tranche', 'Unknown')
                img_name = meta.get('image_file', '')
                img_path = Path(f"./output/{tranche}/{img_name}")
                if img_path.exists():
                     generated_images.append({
                        'filename': img_name,
                        'path': f"{tranche}/{img_name}",
                        'model_id': meta.get('model_id', meta.get('model', 'unknown')),
                        'engine_version': meta.get('engine_version', 'v1'),
                        'prompts': meta.get('prompts', {})
                     })
            except Exception as e:
                print(f"Error reading log {log_file}: {e}")

    return jsonify({
        'cupid_name': cupid_name,
        'product_name': features.get('product_name', ''),
        'brand': features.get('brand', ''),
        'class_description': features.get('class_description', ''),
        'tranche': product.get('Tranche', ''),
        'ghost_images': ghost_urls,
        'generated_images': sorted(generated_images, key=lambda x: x['filename']),
        'specifications': features.get('specifications', {})
    })

@app.route('/api/generate', methods=['POST'])
def generate_api():
    data = request.json
    cupid = data.get('cupid_name')
    active_sources = data.get('active_sources')  # Get list of selected image URLs
    
    if not cupid:
        return jsonify({'success': False, 'error': 'Missing cupid_name'})
    try:
        # Select workflow based on engine config
        if ENGINE_VERSION == 'v2_nanobananapro':
            wf = create_workflow_v2()
            print(f"[Engine: V2 Nano Banana Pro]")
        else:
            wf = create_workflow()
            print(f"[Engine: V1]")
        
        # Pass the list of selected URLs to the workflow
        result = wf.run(cupid, verbose=True, selected_ghost_urls=active_sources)
        result['engine_used'] = ENGINE_VERSION
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'engine_used': ENGINE_VERSION})

@app.route('/output/<path:filename>')
def serve_image(filename):
    return send_from_directory('./output', filename)

def main():
    print("🎯 AI Imagery Workbench (React) running on port 8080")
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    main()

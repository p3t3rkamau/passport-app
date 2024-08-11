from flask import Blueprint, jsonify
import json
import os

sizes_blueprint = Blueprint('sizes', __name__)

@sizes_blueprint.route('/api/sizes', methods=['GET'])
def get_sizes():
    sizes_path = './sizes.json'
    if not os.path.exists(sizes_path):
        return jsonify({"error": "Sizes file not found"}), 404

    with open(sizes_path, 'r') as file:
        sizes = json.load(file)

    if isinstance(sizes, list):
        return jsonify({"error": "Invalid data format"}), 500

    formatted_sizes = [{"label": f"{v['width']}x{v['height']} inches", "value": k} for k, v in sizes.items()]
    return jsonify(formatted_sizes)

import os
import json
import uuid
import math
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from firebase_config import db, initialize_firebase
from models import User
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret-key-please-change')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # Default 16MB

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Initialize Firebase
initialize_firebase()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat/2) * math.sin(dlat/2) + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2) * math.sin(dlon/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

@login_manager.user_loader
def load_user(user_id):
    result = db.get_data(f'users/{user_id}')
    if result['success'] and result['data']:
        return User(result['data'])
    return None

# Firebase CRUD endpoints
@app.route('/products', methods=['GET', 'POST'])
def handle_products():
    """Handle products collection"""
    if request.method == 'GET':
        result = db.get_data('products')
        if result['success']:
            return jsonify({'success': True, 'products': result['data'] or {}})
        return jsonify({'success': False, 'error': result['error']})
    
    elif request.method == 'POST':
        product_data = request.get_json()
        if not product_data:
            return jsonify({'success': False, 'error': 'No data provided'})
        
        # Add timestamp
        product_data['created_at'] = int(time.time() * 1000)
        
        # Generate ID if not provided
        product_id = product_data.get('id', str(int(time.time() * 1000)))
        result = db.save_data(f'products/{product_id}', product_data)
        
        if result['success']:
            return jsonify({'success': True, 'id': product_id, 'data': result['data']})
        return jsonify({'success': False, 'error': result['error']})

@app.route('/products/<product_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_product(product_id):
    """Handle individual product"""
    if request.method == 'GET':
        result = db.get_data(f'products/{product_id}')
        if result['success']:
            if not result['data']:
                return jsonify({'success': False, 'error': 'Product not found'}), 404
            return jsonify({'success': True, 'product': result['data']})
        return jsonify({'success': False, 'error': result['error']})
    
    elif request.method == 'PUT':
        product_data = request.get_json()
        if not product_data:
            return jsonify({'success': False, 'error': 'No data provided'})
        
        # Add update timestamp
        product_data['updated_at'] = int(time.time() * 1000)
        
        result = db.save_data(f'products/{product_id}', product_data)
        if result['success']:
            return jsonify({'success': True, 'data': result['data']})
        return jsonify({'success': False, 'error': result['error']})
    
    elif request.method == 'DELETE':
        result = db.save_data(f'products/{product_id}', None)
        if result['success']:
            return jsonify({'success': True, 'message': 'Product deleted'})
        return jsonify({'success': False, 'error': result['error']})

@app.route('/categories', methods=['GET', 'POST'])
def handle_categories():
    """Handle categories collection"""
    if request.method == 'GET':
        result = db.get_data('categories')
        if result['success']:
            return jsonify({'success': True, 'categories': result['data'] or {}})
        return jsonify({'success': False, 'error': result['error']})
    
    elif request.method == 'POST':
        category_data = request.get_json()
        if not category_data:
            return jsonify({'success': False, 'error': 'No data provided'})
        
        # Add timestamp
        category_data['created_at'] = int(time.time() * 1000)
        
        # Generate ID if not provided
        category_id = category_data.get('id', str(int(time.time() * 1000)))
        result = db.save_data(f'categories/{category_id}', category_data)
        
        if result['success']:
            return jsonify({'success': True, 'id': category_id, 'data': result['data']})
        return jsonify({'success': False, 'error': result['error']})

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000) 
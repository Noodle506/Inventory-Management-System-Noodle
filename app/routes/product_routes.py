from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Product

# FIX: Removed the redundant '/api/products' prefix
bp = Blueprint('products', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
def get_products():
    """Get all products"""
    try:
        products = Product.query.all()
        products_list = [{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': float(p.price), # Ensure price is JSON serializable
            'quantity': p.quantity,
            'sku': p.sku
        } for p in products]
        return jsonify(products_list), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve products', 'details': str(e)}), 500

@bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """Get product by ID"""
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'price': float(product.price),
        'sku': product.sku
    }), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    """Create new product"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'price', 'sku']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if SKU exists
        sku = data['sku'].strip().upper()
        if Product.query.filter_by(sku=sku).first():
            return jsonify({'error': 'SKU already exists'}), 409

        new_product = Product(
            name=data['name'].strip(),
            price=data['price'],
            sku=sku,
            description=data.get('description', ''),
            quantity=data.get('quantity', 0)
        )

        db.session.add(new_product)
        db.session.commit()

        # IMPORTANT: The test expects 'id' in the response body
        return jsonify({
            'message': 'Product created',
            'id': new_product.id,
            'name': new_product.name
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update product"""
    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    if 'name' in data: product.name = data['name']
    if 'price' in data: product.price = data['price']
    
    db.session.commit()
    return jsonify({'message': 'Product updated'}), 200

@bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Delete product"""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    # 204 No Content is standard for delete, but if your test expects 200, use 200
    return '', 204

from flask import Blueprint, request, jsonify, render_template
from app.utils import login_required
from app import db
from app.models import Product

bp = Blueprint('products', __name__)

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'price': float(product.price),
        'quantity': product.quantity,
        'sku': product.sku
    })

# --- VIEW ROUTE ---
# Access this at: /api/products/view
@bp.route('/view', methods=['GET'])
@login_required
def products_view():
    all_products = Product.query.all()
    return render_template('products.html', products=all_products)

# --- API ENDPOINTS ---

@bp.route('', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': float(p.price),
        'quantity': p.quantity,
        'sku': p.sku
    } for p in products]), 200

@bp.route('', methods=['POST'])
def create_product():
    data = request.get_json()
    try:
        new_product = Product(
            name=data['name'].strip(),
            price=data['price'],
            sku=data['sku'].strip().upper(),
            quantity=data.get('quantity', 0)
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'id': new_product.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'SKU must be unique'}), 400

@bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    product.quantity = data.get('quantity', product.quantity)
    
    db.session.commit()
    return jsonify({'message': 'Updated'}), 200

@bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return '', 204
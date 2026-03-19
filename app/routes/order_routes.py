from flask import Blueprint, request, jsonify

bp = Blueprint('orders', __name__, url_prefix='/api/orders')

@bp.route('', methods=['GET'])
def get_orders():
    """Get all orders"""
    # TODO: Implement order retrieval
    return jsonify({'message': 'Get all orders'}), 200

@bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get order by ID"""
    # TODO: Implement order retrieval by ID
    return jsonify({'message': f'Get order {order_id}'}), 200

@bp.route('', methods=['POST'])
def create_order():
    """Create new order"""
    data = request.get_json()
    # TODO: Implement order creation
    return jsonify({'message': 'Create order'}), 201

@bp.route('/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """Update order"""
    data = request.get_json()
    # TODO: Implement order update
    return jsonify({'message': f'Update order {order_id}'}), 200

@bp.route('/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Delete order"""
    # TODO: Implement order deletion
    return jsonify({'message': f'Delete order {order_id}'}), 200

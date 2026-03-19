from flask import Blueprint, request, jsonify

bp = Blueprint('customers', __name__, url_prefix='/api/customers')

@bp.route('', methods=['GET'])
def get_customers():
    """Get all customers"""
    # TODO: Implement customer retrieval
    return jsonify({'message': 'Get all customers'}), 200

@bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get customer by ID"""
    # TODO: Implement customer retrieval by ID
    return jsonify({'message': f'Get customer {customer_id}'}), 200

@bp.route('', methods=['POST'])
def create_customer():
    """Create new customer"""
    data = request.get_json()
    # TODO: Implement customer creation
    return jsonify({'message': 'Create customer'}), 201

@bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update customer"""
    data = request.get_json()
    # TODO: Implement customer update
    return jsonify({'message': f'Update customer {customer_id}'}), 200

@bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Delete customer"""
    # TODO: Implement customer deletion
    return jsonify({'message': f'Delete customer {customer_id}'}), 200

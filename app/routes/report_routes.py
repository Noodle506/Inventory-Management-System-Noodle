from flask import Blueprint, request, jsonify

bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@bp.route('/inventory', methods=['GET'])
def inventory_report():
    """Get inventory report"""
    # TODO: Implement inventory report
    return jsonify({'message': 'Inventory report'}), 200

@bp.route('/sales', methods=['GET'])
def sales_report():
    """Get sales report"""
    # TODO: Implement sales report
    return jsonify({'message': 'Sales report'}), 200

@bp.route('/customers', methods=['GET'])
def customer_report():
    """Get customer report"""
    # TODO: Implement customer report
    return jsonify({'message': 'Customer report'}), 200

@bp.route('/orders', methods=['GET'])
def order_report():
    """Get order report"""
    # TODO: Implement order report
    return jsonify({'message': 'Order report'}), 200

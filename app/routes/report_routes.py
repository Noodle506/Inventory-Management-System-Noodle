from flask import Blueprint, jsonify, render_template
from app.utils import login_required
from app.models import Product, Customer, Order
from sqlalchemy import func
from app import db

bp = Blueprint('reports', __name__)

@bp.route('/view', methods=['GET'])
@login_required
def reports_page():
    return render_template('reports.html')

@bp.route('/inventory', methods=['GET'])
def inventory_report():
    low_stock_products = Product.query.filter(Product.quantity < 5).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'quantity': p.quantity
    } for p in low_stock_products]), 200

@bp.route('/sales', methods=['GET'])
def sales_report():
    total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0
    total_orders = Order.query.count()
    return jsonify({
        'total_revenue': float(total_revenue),
        'total_orders': total_orders
    }), 200

@bp.route('/customers', methods=['GET'])
def customer_report():
    customers = Customer.query.all()
    output = []
    for c in customers:
        output.append({
            'name': c.name,
            'order_count': len(c.orders),
            'city': c.city or "Unknown"
        })
    output.sort(key=lambda x: x['order_count'], reverse=True)
    return jsonify(output), 200

@bp.route('/orders', methods=['GET'])
def order_report():
    # Note: changed .order_date to .id or .created_at based on typical models
    recent_orders = Order.query.order_by(Order.id.desc()).limit(10).all()
    return jsonify([{
        'id': o.id,
        'customer': o.customer.name if o.customer else "Guest",
        'date': o.id, # Placeholder if created_at doesn't exist yet
        'total': float(o.total_amount),
        'status': o.status
    } for o in recent_orders]), 200
from flask import Blueprint, request, jsonify, render_template
from app.utils import login_required
from app import db
from app.models import Customer

bp = Blueprint('customers', __name__)

# --- VIEW ROUTE ---
# URL: /api/customers/view
@bp.route('/view', methods=['GET'])
@login_required
def customers_view():
    all_customers = Customer.query.all()
    return render_template('customers.html', customers=all_customers)

# --- API ENDPOINTS ---

@bp.route('', methods=['GET'])
def get_customers_api():
    customers = Customer.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'email': c.email,
        'phone': c.phone,
        'city': c.city
    } for c in customers]), 200

@bp.route('', methods=['POST'])
def create_customer():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    try:
        new_customer = Customer(
            name=data.get('name').strip(),
            email=data.get('email', '').strip().lower() if data.get('email') else None,
            phone=data.get('phone'),
            city=data.get('city'),
            address=data.get('address'),
            postal_code=data.get('postal_code')
        )
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({'message': 'Customer created', 'id': new_customer.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create customer', 'details': str(e)}), 500

@bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()
    
    if 'name' in data: customer.name = data['name'].strip()
    if 'email' in data: customer.email = data['email'].strip().lower()
    if 'phone' in data: customer.phone = data['phone']
    if 'city' in data: customer.city = data['city']
    
    try:
        db.session.commit()
        return jsonify({'message': 'Updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    try:
        db.session.delete(customer)
        db.session.commit()
        return '', 204
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Cannot delete customer with order history'}), 500
from flask import Blueprint, request, jsonify, render_template
from app.utils import login_required
from app import db
from app.models import Order, OrderItem, Product, Customer
from app.services.inventory_service import InventoryService
import traceback 

bp = Blueprint('orders', __name__)

@bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    items = [
        {
            'product_id': item.product_id,
            'quantity': item.quantity
        } for item in order.items
    ]
    return jsonify({
        'id': order.id,
        'customer_id': order.customer_id,
        'items': items
    })

@bp.route('/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    customer_id = data.get('customer_id')
    items_data = data.get('items')
    if not customer_id or not items_data:
        return jsonify({'error': 'Please select a customer and at least one product'}), 400
    try:
        # Restore product quantities for old items
        for item in order.items:
            product = Product.query.get(item.product_id)
            if product:
                product.quantity += item.quantity
        # Remove old items
        OrderItem.query.filter_by(order_id=order.id).delete()
        db.session.flush()
        # Update order
        order.customer_id = customer_id
        running_total = 0
        for item in items_data:
            p_id = item['product_id']
            qty = int(item['quantity'])
            product = Product.query.get(p_id)
            if not product or product.quantity < qty:
                db.session.rollback()
                return jsonify({'error': f'Not enough stock for {product.name if product else p_id}'}), 400
            product.quantity -= qty
            item_total = float(product.price) * qty
            running_total += item_total
            order_item = OrderItem(
                order_id=order.id,
                product_id=p_id,
                quantity=qty,
                unit_price=product.price,
                total_price=item_total
            )
            db.session.add(order_item)
        order.total_amount = running_total
        db.session.commit()
        return jsonify({'message': 'Order updated'}), 200
    except Exception as e:
        db.session.rollback()
        print(traceback.format_exc())
        return jsonify({'error': 'Server Error', 'details': str(e)}), 500
from flask import Blueprint, request, jsonify, render_template
from app import db
from app.models import Order, OrderItem, Product, Customer
from app.services.inventory_service import InventoryService
import traceback 

bp = Blueprint('orders', __name__)

# --- VIEW ROUTE ---
# Access at: /api/orders/view
@bp.route('/view', methods=['GET'])
@login_required
def orders_view():
    """Render the HTML page for orders"""
    all_orders = Order.query.order_by(Order.id.desc()).all()
    all_customers = Customer.query.all()
    all_products = Product.query.all()
    return render_template('orders.html', 
                           orders=all_orders, 
                           customers=all_customers, 
                           products=all_products)

# --- API ENDPOINTS ---

@bp.route('', methods=['POST'])
def create_order():
    data = request.get_json()
    customer_id = data.get('customer_id')
    items_data = data.get('items') 

    if not customer_id or not items_data:
        return jsonify({'error': 'Please select a customer and at least one product'}), 400

    try:
        # 1. Start the Order
        new_order = Order(customer_id=customer_id, total_amount=0, status='pending')
        db.session.add(new_order)
        db.session.flush() # Gets the ID without a full commit yet

        running_total = 0

        for item in items_data:
            p_id = item['product_id']
            qty = int(item['quantity'])

            # 2. Check Availability
            product = db.session.get(Product, p_id)
            if not product or product.quantity < qty:
                db.session.rollback()
                return jsonify({'error': f'Not enough stock for {product.name if product else p_id}'}), 400

            # 3. Deduct Stock & Calculate Price
            product.quantity -= qty
            item_total = float(product.price) * qty
            running_total += item_total

            # 4. Create OrderItem
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=p_id,
                quantity=qty,
                unit_price=product.price,
                total_price=item_total
            )
            db.session.add(order_item)

        # 5. Finalize
        new_order.total_amount = running_total
        new_order.status = 'completed'
        db.session.commit()

        return jsonify({'message': 'Order successful', 'order_id': new_order.id}), 201

    except Exception as e:
        db.session.rollback()
        print(traceback.format_exc()) 
        return jsonify({'error': 'Server Error', 'details': str(e)}), 500

@bp.route('/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    try:
        db.session.delete(order)
        db.session.commit()
        return '', 204
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete order'}), 500
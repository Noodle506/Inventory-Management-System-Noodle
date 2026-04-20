from app import db
from app.models import Order, OrderItem, Product

class OrderService:
    """Service for order operations"""
    
    @staticmethod
    def create_order(customer_id, items):
        """Create a new order"""
        # TODO: Implement order creation logic
        pass
    
    @staticmethod
    def update_order(order_id, data):
        """Update an existing order"""
        from app.models.order import Order
        from app.models.order_item import OrderItem
        from app.models.product import Product
        from app import db
        import traceback
        order = Order.query.get_or_404(order_id)
        customer_id = data.get('customer_id')
        items_data = data.get('items')
        if not customer_id or not items_data:
            return {'error': 'Please select a customer and at least one product'}, 400
        try:
            # Restore product quantities for old items
            for item in order.order_items:
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
                    return {'error': f'Not enough stock for {product.name if product else p_id}'}, 400
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
            return {'message': 'Order updated'}, 200
        except Exception as e:
            db.session.rollback()
            print(traceback.format_exc())
            return {'error': 'Server Error', 'details': str(e)}, 500
    
    @staticmethod
    def cancel_order(order_id):
        """Cancel an order"""
        # TODO: Implement order cancellation logic
        pass
    
    @staticmethod
    def get_order_total(order_id):
        """Calculate order total"""
        # TODO: Implement order total calculation
        pass

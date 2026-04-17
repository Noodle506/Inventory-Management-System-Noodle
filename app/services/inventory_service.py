from app import db
from app.models import Product

class InventoryService:
    """Service for inventory operations - Milestone 2 Final"""
    
    @staticmethod
    def update_stock(product_id, quantity_change):
        # Use session.get (SQLAlchemy 2.0)
        product = db.session.get(Product, product_id)
        if product:
            # FIX: Changed .stock to .quantity
            product.quantity += quantity_change
            try:
                db.session.commit()
                return True
            except Exception:
                db.session.rollback()
                return False
        return False
    
    @staticmethod
    def check_availability(product_id, requested_quantity):
        product = db.session.get(Product, product_id)
        if not product:
            return False
        # FIX: Changed .stock to .quantity
        return product.quantity >= requested_quantity
    
    @staticmethod
    def get_low_stock_items(threshold=5):
        # FIX: Changed .stock to .quantity
        return Product.query.filter(Product.quantity <= threshold).all()
    
    @staticmethod
    def reserve_stock(product_id, quantity):
        product = db.session.get(Product, product_id)
        # FIX: Changed .stock to .quantity
        if product and product.quantity >= quantity:
            product.quantity -= quantity
            # We don't commit here; the route handles the transaction
            return True
        return False
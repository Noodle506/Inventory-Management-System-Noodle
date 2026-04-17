import unittest
import json
import random
import string
from app import create_app, db
from app.models import User, Product, Customer, Order, OrderItem 

class Milestone2TestCase(unittest.TestCase):
    def setUp(self):
        """Initialize the app and context for Supabase testing"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Ensures your Supabase tables are ready
        db.create_all()

    def tearDown(self):
        """Cleanup after the test finishes"""
        db.session.remove()
        self.app_context.pop()

    def get_token(self):
        """Helper to handle Authentication flow"""
        reg_payload = {
            "username": "tester_m2", 
            "email": "m2@example.com",
            "password": "StrongPassword123"
        }
        # Attempt registration (ignore failure if user already exists)
        self.client.post('/api/auth/register', json=reg_payload)
        
        # Login to get the JWT
        res_login = self.client.post('/api/auth/login', json=reg_payload)
        if res_login.status_code == 200:
            return json.loads(res_login.data).get('access_token')
        return None

    def test_inventory_deduction_logic(self):
        """Core Logic: Create Product -> Place Order -> Verify Stock Deduction"""
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'} if token else {}

        # 1. Generate a unique SKU to prevent Database UniqueConstraint errors
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        unique_sku = f"TEST-WATCH-{suffix}"
        
        # 2. Setup Test Product (Start with 15 units)
        prod = Product(
            name=f"Automated Test Watch {suffix}", 
            price=199.99, 
            sku=unique_sku, 
            quantity=15
        )
        
        # 3. Setup or Retrieve Test Customer
        cust_email = "tester_ui@example.com"
        cust = Customer.query.filter_by(email=cust_email).first()
        if not cust:
            cust = Customer(name="Yadid Test Bot", email=cust_email, city="Fajardo")
            db.session.add(cust)
        
        db.session.add(prod)
        db.session.commit()

        # 4. Define Order Payload (Buy 3 units)
        order_payload = {
            "customer_id": cust.id,
            "items": [{"product_id": prod.id, "quantity": 3}]
        }
        
        # 5. Execute the Order POST request
        res_order = self.client.post('/api/orders', json=order_payload, headers=headers)
        
        # 6. Verify API Success
        self.assertEqual(res_order.status_code, 201, f"API Error: {res_order.data.decode()}")
        
        # 7. Verify Database Logic (15 - 3 = 12)
        db.session.refresh(prod) 
        self.assertEqual(prod.quantity, 12, f"Stock logic failed! Expected 12, got {prod.quantity}")
        
        # 8. Success Output
        order_data = json.loads(res_order.data)
        print(f"\n🚀 TEST SUCCESS")
        print(f"📦 Created Order #{order_data['order_id']}")
        print(f"📉 Stock for {prod.name} successfully dropped to {prod.quantity}")

        # --- LINE 90: THE BREAKPOINT ---
        # While the terminal is paused at (Pdb), refresh your browser 
        # at http://127.0.0.1:5000/api/orders/view to see this order!
        import pdb; pdb.set_trace() 

if __name__ == '__main__':
    unittest.main()
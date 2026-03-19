import unittest
import json
from app import create_app, db
from app.models import User, Product

class Milestone1TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # --- HELPER METHOD (Not a test itself) ---
    def get_token(self):
        """Helper to register and login a user to get a JWT"""
        reg_payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123"
        }
        self.client.post('/auth/register', json=reg_payload)
        
        res_login = self.client.post('/auth/login', json=reg_payload)
        data = json.loads(res_login.data)
        return data['access_token']

    # --- ACTUAL TESTS ---

    def test_database_connection(self):
        """T2: PostgreSQL Schema"""
        users = User.query.all()
        self.assertEqual(users, [])

    def test_authentication(self):
        """T3: Authentication"""
        reg_payload = {
            "username": "authuser",
            "email": "auth@example.com",
            "password": "StrongPassword123"
        }
        res_reg = self.client.post('/auth/register', json=reg_payload)
        self.assertEqual(res_reg.status_code, 201)

    def test_product_crud(self):
        """T4: Product CRUD - Full lifecycle test"""
        token = self.get_token() # Use the helper
        headers = {'Authorization': f'Bearer {token}'}

        # 1. Create
        new_prod = {
            "name": "Test Gadget", 
            "price": 99.99, 
            "sku": "GADGET-001"
        }
        res_create = self.client.post('/products', json=new_prod, headers=headers)
        self.assertEqual(res_create.status_code, 201)
        
        data = json.loads(res_create.data)
        
        # FIX: Check if 'id' is in the root OR inside the 'product' dictionary
        if 'product' in data:
            product_id = data['product']['id']
        else:
            product_id = data['id']

        # 2. Read
        res_get = self.client.get(f'/products/{product_id}', headers=headers)
        self.assertEqual(res_get.status_code, 200)
        
        # 3. Update
        update_data = {"price": 79.99}
        res_put = self.client.put(f'/products/{product_id}', json=update_data, headers=headers)
        self.assertEqual(res_put.status_code, 200)

       # 4. Delete
        res_del = self.client.delete(f'/products/{product_id}', headers=headers)
        # Accepts 204 (No Content) or 200 (OK)
        self.assertIn(res_del.status_code, [200, 204])

if __name__ == '__main__':
    unittest.main()
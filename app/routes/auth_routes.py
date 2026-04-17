from flask import Blueprint, request, jsonify, render_template, session  # Fixed: Added render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
import re

# NOTE: url_prefix is handled centrally in app/__init__.py

bp = Blueprint('auth', __name__)

@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return '', 204

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

# --- VIEW ROUTES (GET) ---

@bp.route('/register', methods=['GET'])
def register_page():
    """Render the Register HTML page"""
    return render_template('register.html')

@bp.route('/login', methods=['GET'])
def login_page():
    """Render the Login HTML page"""
    return render_template('login.html')

# --- API ENDPOINTS (POST) ---

@bp.route('/register', methods=['POST'])
def register():
    """User registration logic"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']

        # Validations
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return jsonify({'error': 'Invalid email format'}), 400

        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400

        # Check existing
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409

        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 409

        # Create user
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        # Create token
        access_token = create_access_token(identity=str(username))

        return jsonify({
            'message': 'User registered successfully',
            'id': new_user.id,
            'access_token': access_token
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """User login logic"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            return jsonify({'error': 'Invalid username or password'}), 401

        # Create token
        access_token = create_access_token(identity=str(user.username))
        session['username'] = user.username
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token
        }), 200

    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

# Initialize extensions outside the factory to avoid circular imports
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_class='app.config.Config'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)

    # Initialize extensions with the app instance
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)  # Enable CORS for API access

    # Import blueprints inside the function to prevent circular imports
    from app.routes import (
        auth_routes, 
        product_routes, 
        customer_routes, 
        order_routes, 
        report_routes
    )

    # Register blueprints with proper URL prefixes for Milestone 1 / T4
    # This maps the routes so the test client can find them
    app.register_blueprint(auth_routes.bp, url_prefix='/auth')
    app.register_blueprint(product_routes.bp, url_prefix='/products')
    app.register_blueprint(customer_routes.bp, url_prefix='/customers')
    app.register_blueprint(order_routes.bp, url_prefix='/orders')
    app.register_blueprint(report_routes.bp, url_prefix='/reports')

    # Create database tables (T2: PostgreSQL Schema)
    with app.app_context():
        db.create_all()

    return app
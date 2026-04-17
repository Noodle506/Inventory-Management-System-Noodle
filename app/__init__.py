from flask import Flask, redirect, url_for  # Added redirect/url_for
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

# 1. Initialize extensions globally
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_class='app.config.Config'):
    app = Flask(__name__)

    # Make session['username'] available in all templates
    @app.context_processor
    def inject_user():
        from flask import session
        return dict(session=session)

    # 2. Load configuration
    app.config.from_object(config_class)

    # 3. Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # 4. Import and Register Blueprints
    from app.routes import (
        auth_routes, 
        product_routes, 
        customer_routes, 
        order_routes, 
        report_routes
    )

    app.register_blueprint(auth_routes.bp, url_prefix='/api/auth')
    app.register_blueprint(product_routes.bp, url_prefix='/api/products')
    app.register_blueprint(customer_routes.bp, url_prefix='/api/customers')
    app.register_blueprint(order_routes.bp, url_prefix='/api/orders')
    app.register_blueprint(report_routes.bp, url_prefix='/api/reports')

    # --- HOME ROUTE: Render index.html as the home page ---
    from flask import render_template
    from app.utils import login_required
    @app.route('/')
    @login_required
    def home():
        from app.models import Product, Customer, Order
        products_count = Product.query.count()
        customers_count = Customer.query.count()
        orders_count = Order.query.count()
        return render_template(
            'index.html',
            products_count=products_count,
            customers_count=customers_count,
            orders_count=orders_count
        )

    # 5. Create Database Tables
    with app.app_context():
        db.create_all()

    return app
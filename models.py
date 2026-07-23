 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    """Healthcare products and services"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.String(300))
    price = db.Column(db.Float, nullable=False)
    discount_percentage = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(100), nullable=False)
    subcategory = db.Column(db.String(100))
    image_url = db.Column(db.String(500))
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    @property
    def discounted_price(self):
        if self.discount_percentage > 0:
            return round(self.price * (1 - self.discount_percentage / 100), 2)
        return self.price
    
    @property
    def savings(self):
        if self.discount_percentage > 0:
            return round(self.price - self.discounted_price, 2)
        return 0

class Order(db.Model):
    """Customer orders"""
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_email = db.Column(db.String(200), nullable=False)
    customer_phone = db.Column(db.String(50))
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    payment_method = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderItem(db.Model):
    """Individual items within an order"""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_at_time = db.Column(db.Float, nullable=False)
    product_name = db.Column(db.String(200))
    
    product = db.relationship('Product')
    
    @property
    def subtotal(self):
        return self.quantity * self.price_at_time

class InsightArticle(db.Model):
    """Blog/resources articles"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(300))
    category = db.Column(db.String(100))
    author = db.Column(db.String(100))
    image_url = db.Column(db.String(500))
    published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Article {self.title}>'
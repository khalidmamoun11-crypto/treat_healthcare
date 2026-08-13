from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets
import os

app = Flask(__name__)
app.secret_key = 'treat_healthcare_advanced_secret_key_2026'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///treat_healthcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)

# ---------- DATABASE MODELS ----------
class Product(db.Model):
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
    stock_quantity = db.Column(db.Integer, default=999)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    payment_method = db.Column(db.String(50), default='invoice')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_at_time = db.Column(db.Float, nullable=False)
    product_name = db.Column(db.String(200))
    product = db.relationship('Product')

class InsightArticle(db.Model):
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

# ---------- HELPER FUNCTIONS ----------
def get_cart_items():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.discounted_price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': round(item_total, 2)
            })
    return cart_items, round(total, 2)

def cart_count():
    cart = session.get('cart', {})
    return sum(cart.values())

# ---------- ROUTES ----------
@app.route('/')
def index():
    featured_products = Product.query.filter_by(featured=True).limit(6).all()
    return render_template('index.html', featured_products=featured_products)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/plans')
def plans_catalog():
    category = request.args.get('category')
    if category:
        products = Product.query.filter_by(category=category).all()
    else:
        products = Product.query.all()
    categories = db.session.query(Product.category).distinct().all()
    return render_template('plans_catalog.html', 
                         products=products, 
                         categories=[c[0] for c in categories],
                         selected_category=category)

@app.route('/plan/<slug>')
def plan_detail(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    related = Product.query.filter(
        Product.category == product.category,
        Product.id != product.id
    ).limit(4).all()
    return render_template('plan_detail.html', product=product, related=related)

@app.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    flash(f'✅ {product.name} added to your cart!', 'success')
    return redirect(request.referrer or url_for('plans_catalog'))

@app.route('/cart')
def view_cart():
    cart_items, total = get_cart_items()
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update-cart', methods=['POST'])
def update_cart():
    cart = session.get('cart', {})
    product_id = request.form.get('product_id')
    action = request.form.get('action')
    
    if product_id in cart:
        if action == 'increase':
            cart[product_id] += 1
        elif action == 'decrease':
            cart[product_id] -= 1
            if cart[product_id] <= 0:
                del cart[product_id]
        elif action == 'remove':
            del cart[product_id]
    
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart_items, total = get_cart_items()
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('plans_catalog'))
    
    if request.method == 'POST':
        order_number = f"TREAT-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        
        order = Order(
            order_number=order_number,
            customer_name=request.form.get('name'),
            customer_email=request.form.get('email'),
            customer_phone=request.form.get('phone'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            country=request.form.get('country'),
            total_amount=total,
            payment_method=request.form.get('payment_method', 'invoice'),
            notes=request.form.get('notes')
        )
        db.session.add(order)
        db.session.flush()
        
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price_at_time=item['product'].discounted_price,
                product_name=item['product'].name
            )
            db.session.add(order_item)
        
        db.session.commit()
        session['cart'] = {}
        
        flash(f'✅ Order {order_number} confirmed!', 'success')
        return render_template('order_confirmation.html', order=order, items=cart_items, total=total)
    
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/insights')
def insights():
    articles = InsightArticle.query.filter_by(published=True).order_by(InsightArticle.created_at.desc()).all()
    return render_template('insights.html', articles=articles)

@app.route('/insight/<slug>')
def insight_detail(slug):
    article = InsightArticle.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template('insight_detail.html', article=article)

@app.route('/services/international-insurance')
def service_international():
    products = Product.query.filter_by(category='International Insurance').all()
    return render_template('services/international_insurance.html', products=products)

@app.route('/services/global-medical-access')
def service_medical_access():
    products = Product.query.filter_by(category='Global Medical Access').all()
    return render_template('services/global_medical_access.html', products=products)

@app.route('/services/cross-border-staffing')
def service_staffing():
    products = Product.query.filter_by(category='Cross-Border Staffing').all()
    return render_template('services/cross_border_staffing.html', products=products)

# ---------- ADMIN ROUTES ----------
@app.route('/admin')
def admin_dashboard():
    products = Product.query.all()
    orders = Order.query.order_by(Order.created_at.desc()).limit(20).all()
    articles = InsightArticle.query.order_by(InsightArticle.created_at.desc()).limit(10).all()
    
    stats = {
        'total_products': Product.query.count(),
        'total_orders': Order.query.count(),
        'total_articles': InsightArticle.query.count(),
        'revenue': db.session.query(db.func.sum(Order.total_amount)).scalar() or 0,
        'pending_orders': Order.query.filter_by(status='pending').count()
    }
    return render_template('admin/dashboard.html', 
                         products=products, 
                         orders=orders, 
                         articles=articles,
                         stats=stats)

@app.route('/admin/product/new', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product = Product(
            name=request.form.get('name'),
            slug=request.form.get('name').lower().replace(' ', '-'),
            description=request.form.get('description'),
            short_description=request.form.get('short_description'),
            price=float(request.form.get('price', 0)),
            discount_percentage=float(request.form.get('discount_percentage', 0)),
            category=request.form.get('category'),
            subcategory=request.form.get('subcategory'),
            image_url=request.form.get('image_url'),
            featured=bool(request.form.get('featured', False)),
            stock_quantity=int(request.form.get('stock_quantity', 999))
        )
        db.session.add(product)
        db.session.commit()
        flash('✅ Product added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_product.html', product=None)

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.slug = request.form.get('name').lower().replace(' ', '-')
        product.description = request.form.get('description')
        product.short_description = request.form.get('short_description')
        product.price = float(request.form.get('price', 0))
        product.discount_percentage = float(request.form.get('discount_percentage', 0))
        product.category = request.form.get('category')
        product.subcategory = request.form.get('subcategory')
        product.image_url = request.form.get('image_url')
        product.featured = bool(request.form.get('featured', False))
        product.stock_quantity = int(request.form.get('stock_quantity', 999))
        db.session.commit()
        flash('✅ Product updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_product.html', product=product)

@app.route('/admin/product/delete/<int:product_id>')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('🗑️ Product deleted', 'warning')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/order/<int:order_id>')
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/view_order.html', order=order)

@app.route('/admin/order/update/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form.get('status')
    db.session.commit()
    flash(f'✅ Order status updated to {order.status}', 'success')
    return redirect(url_for('admin_dashboard'))

# ---------- CONTEXT PROCESSOR ----------
@app.context_processor
def utility_processor():
    return dict(cart_count=cart_count, now=datetime.utcnow)

# ---------- INITIALIZE DATABASE ----------
def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Add sample products if none exist
        if Product.query.count() == 0:
            print("📦 Adding sample products...")
            sample_products = [
                Product(
                    name='Global Explorer Insurance',
                    slug='global-explorer-insurance',
                    description='Comprehensive international health insurance covering routine care, hospital stays, and emergency medical evacuation worldwide.',
                    short_description='Full coverage for global citizens',
                    price=499.99,
                    discount_percentage=12,
                    category='International Insurance',
                    subcategory='Comprehensive',
                    image_url='https://via.placeholder.com/600x400/1a5276/ffffff?text=Global+Explorer',
                    featured=True,
                    stock_quantity=100
                ),
                Product(
                    name='Expatriate Complete Care',
                    slug='expatriate-complete-care',
                    description='Full-spectrum international insurance for expatriates. Includes routine checkups, specialist consultations, hospitalizations, and air ambulance evacuation.',
                    short_description='Complete care for expats',
                    price=699.99,
                    discount_percentage=18,
                    category='International Insurance',
                    subcategory='Expat',
                    image_url='https://via.placeholder.com/600x400/2e86c1/ffffff?text=Expat+Complete',
                    featured=True,
                    stock_quantity=100
                ),
                Product(
                    name='Emergency Evacuation Plus',
                    slug='emergency-evacuation-plus',
                    description='Specialized coverage focused on emergency medical evacuation, repatriation, and transport to top-tier medical facilities worldwide.',
                    short_description='Emergency protection anywhere',
                    price=249.99,
                    discount_percentage=8,
                    category='International Insurance',
                    subcategory='Emergency',
                    image_url='https://via.placeholder.com/600x400/e74c3c/ffffff?text=Evacuation+Plus',
                    featured=False,
                    stock_quantity=100
                ),
                Product(
                    name='Top Clinics Passport',
                    slug='top-clinics-passport',
                    description='Grants access to top-tier clinics and specialist doctors in over 30 countries. Includes treatment coordination and concierge medical travel.',
                    short_description='Access to world-class clinics',
                    price=899.99,
                    discount_percentage=15,
                    category='Global Medical Access',
                    subcategory='Clinic Access',
                    image_url='https://via.placeholder.com/600x400/8e44ad/ffffff?text=Top+Clinics',
                    featured=True,
                    stock_quantity=50
                ),
                Product(
                    name='Second Opinion Global',
                    slug='second-opinion-global',
                    description='Connect with world-renowned specialists for second opinions on complex diagnoses. Access to Mayo Clinic, Cleveland Clinic, and leading European hospitals.',
                    short_description='Expert second opinions',
                    price=349.99,
                    discount_percentage=10,
                    category='Global Medical Access',
                    subcategory='Second Opinions',
                    image_url='https://via.placeholder.com/600x400/3498db/ffffff?text=Second+Opinion',
                    featured=False,
                    stock_quantity=50
                ),
                Product(
                    name='Medical Tourism Concierge',
                    slug='medical-tourism-concierge',
                    description='Full-service medical tourism package including treatment planning, travel arrangements, accommodation, and post-care follow-up at JCI-accredited international hospitals.',
                    short_description='Complete medical travel service',
                    price=1299.99,
                    discount_percentage=20,
                    category='Global Medical Access',
                    subcategory='Medical Tourism',
                    image_url='https://via.placeholder.com/600x400/2ecc71/ffffff?text=Medical+Tourism',
                    featured=False,
                    stock_quantity=30
                ),
                Product(
                    name='Nurse Relocation Program',
                    slug='nurse-relocation-program',
                    description='Complete recruitment and relocation package for registered nurses. Includes licensing assistance, visa processing, housing support, and cultural orientation.',
                    short_description='Comprehensive nurse relocation',
                    price=2499.99,
                    discount_percentage=5,
                    category='Cross-Border Staffing',
                    subcategory='Nurse Recruitment',
                    image_url='https://via.placeholder.com/600x400/f39c12/ffffff?text=Nurse+Relocation',
                    featured=False,
                    stock_quantity=20
                ),
                Product(
                    name='Medical Expert Placement',
                    slug='medical-expert-placement',
                    description='Executive recruitment for specialized physicians, surgeons, and healthcare administrators. Global talent sourcing with full credential verification.',
                    short_description='Executive medical recruitment',
                    price=4999.99,
                    discount_percentage=5,
                    category='Cross-Border Staffing',
                    subcategory='Executive Search',
                    image_url='https://via.placeholder.com/600x400/d35400/ffffff?text=Expert+Placement',
                    featured=True,
                    stock_quantity=20
                ),
                Product(
                    name='Temporary Staffing Pool',
                    slug='temporary-staffing-pool',
                    description='On-demand access to pre-vetted international healthcare professionals for short-term assignments. Ideal for covering staffing shortages during crises.',
                    short_description='Flexible staffing solutions',
                    price=1499.99,
                    discount_percentage=8,
                    category='Cross-Border Staffing',
                    subcategory='Temporary Staffing',
                    image_url='https://via.placeholder.com/600x400/16a085/ffffff?text=Temporary+Staffing',
                    featured=False,
                    stock_quantity=50
                )
            ]
            for p in sample_products:
                db.session.add(p)
            db.session.commit()
            print(f"✅ {len(sample_products)} sample products created!")
        
        # Add sample articles if none exist
        if InsightArticle.query.count() == 0:
            print("📝 Adding sample articles...")
            sample_articles = [
                InsightArticle(
                    title='Beyond Borders: Understanding Global Healthcare Networks',
                    slug='beyond-borders-global-healthcare',
                    content='<p>At first glance, a global healthcare network might seem similar to what we know in the U.S.—a group of doctors and hospitals that work with an insurance carrier to provide care at agreed-upon rates. Same idea, just on a larger scale... right?</p><p>Not exactly. Healthcare systems around the world operate differently. That\'s why global networks must take a different approach.</p><h3>Why U.S. healthcare models don\'t translate</h3><p>In the U.S., most people pay a share of the cost when they get care. This includes copays, deductibles, or coinsurance. After a visit, providers send the bill to the insurance company and receive payment later.</p><p>In many other countries, healthcare follows a different model—often run and funded by the government. Doctors and hospitals in those systems usually expect full payment at the time of service.</p>',
                    excerpt='Understanding why global healthcare networks require a fundamentally different approach than U.S.-based models.',
                    category='International Insurance',
                    author='Dr. Sarah Mitchell',
                    image_url='https://via.placeholder.com/800x400/0a2540/ffffff?text=Global+Healthcare+Networks',
                    published=True
                ),
                InsightArticle(
                    title='The Future of Cross-Border Healthcare Staffing',
                    slug='future-cross-border-staffing',
                    content='<p>The global healthcare industry faces an unprecedented talent shortage. By 2030, the World Health Organization projects a shortfall of 10 million healthcare workers worldwide.</p><p>Cross-border staffing has emerged as a critical solution to this challenge, connecting healthcare professionals from countries with surplus talent to regions facing critical shortages.</p>',
                    excerpt='How international recruitment is solving the global healthcare talent shortage.',
                    category='Cross-Border Staffing',
                    author='James Okonkwo',
                    image_url='https://via.placeholder.com/800x400/1a5276/ffffff?text=Cross-Border+Staffing',
                    published=True
                ),
                InsightArticle(
                    title='Navigating Global Medical Access',
                    slug='navigating-global-medical-access',
                    content='<p>Patients today have more options than ever before when it comes to seeking medical treatment abroad. From specialized procedures to cutting-edge clinical trials, global medical access opens doors to care that may not be available locally.</p>',
                    excerpt='A comprehensive guide to accessing world-class healthcare across borders.',
                    category='Global Medical Access',
                    author='Dr. Michael Chen',
                    image_url='https://via.placeholder.com/800x400/27ae60/ffffff?text=Global+Medical+Access',
                    published=True
                )
            ]
            for a in sample_articles:
                db.session.add(a)
            db.session.commit()
            print(f"✅ {len(sample_articles)} sample articles created!")

# Initialize database
print("🚀 Starting database initialization...")
init_db()
print("✅ All done! Starting Flask server...")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Define the models


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    cart_items = db.relationship('CartItem', backref='customer', lazy=True)
    orders = db.relationship('Order', backref='customer', lazy=True)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey(
        'customer.id'), nullable=False)

    product = db.relationship('Product', backref='cart_items', lazy=True)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey(
        'customer.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)


# Initialize the database
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([product.as_dict() for product in products])


@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    product = Product(name=data['name'], price=data['price'])
    db.session.add(product)
    db.session.commit()
    return jsonify(product.as_dict()), 201


@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return jsonify([customer.as_dict() for customer in customers])


@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.get_json()
    customer = Customer(name=data['name'], email=data['email'])
    db.session.add(customer)
    db.session.commit()
    return jsonify(customer.as_dict()), 201


@app.route('/customers/<int:customer_id>/cart', methods=['POST'])
def add_to_cart(customer_id):
    data = request.get_json()
    product_id = data['product_id']
    customer = Customer.query.get(customer_id)
    product = Product.query.get(product_id)
    if customer and product:
        cart_item = CartItem(customer_id=customer.id, product_id=product.id)
        db.session.add(cart_item)
        db.session.commit()
        return jsonify(customer.as_dict()), 201
    return jsonify({'message': 'Customer or Product not found'}), 404


@app.route('/customers/<int:customer_id>/cart', methods=['GET'])
def view_cart(customer_id):
    customer = Customer.query.get(customer_id)
    if customer:
        cart_items = CartItem.query.filter_by(customer_id=customer.id).all()
        products = [item.product for item in cart_items]
        return jsonify([product.as_dict() for product in products])
    return jsonify({'message': 'Customer not found'}), 404


@app.route('/customers/<int:customer_id>/checkout', methods=['POST'])
def checkout(customer_id):
    customer = Customer.query.get(customer_id)
    if customer:
        cart_items = CartItem.query.filter_by(customer_id=customer.id).all()
        if cart_items:
            total = sum(item.product.price for item in cart_items)
            order = Order(customer_id=customer.id, total=total)
            db.session.add(order)
            db.session.commit()
            for item in cart_items:
                order_item = OrderItem(
                    order_id=order.id, product_id=item.product_id, price=item.product.price)
                db.session.add(order_item)
                db.session.delete(item)
            db.session.commit()
            return jsonify(order.as_dict()), 201
    return jsonify({'message': 'Customer not found or cart is empty'}), 404


@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([order.as_dict() for order in orders])


def model_to_dict(model):
    return {column.name: getattr(model, column.name) for column in model.__table__.columns}


Product.as_dict = model_to_dict
Customer.as_dict = model_to_dict
Order.as_dict = model_to_dict

if __name__ == '__main__':
    app.run(debug=True)

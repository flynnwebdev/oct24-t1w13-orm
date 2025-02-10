from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

# DB connection string
# <protocol>://<user>:<pass>@<host>:<port>/<db_name>
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://orm_dev:123456@localhost:5432/orm_db'

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Model
# This just declares and configures the model in memory - the physical DB is unaffected.
class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float(precision=2))
    stock = db.Column(db.Integer, db.CheckConstraint('stock >= 0'))    

# Schema
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'price', 'stock')


@app.route('/')
def home():
    return 'Hello!'

# R - Read (all)
@app.route('/products')
def get_all_products():
    # Generate a statement
    # SELECT * FROM products;
    stmt = db.select(Product)
    # Execute the statement
    products = db.session.scalars(stmt)
    return ProductSchema(many=True).dump(products)

# R - Read (one)
@app.route('/products/<int:product_id>')
def get_one_product(product_id):
    # Get Product with given id
    # SELECT * FROM products WHERE id = product_id;
    stmt = db.select(Product).filter_by(id=product_id)
    product = db.session.scalar(stmt)
    if product:
        return ProductSchema().dump(product)
    else:
        return {"error": f"Product with id {product_id} not found"}, 404

# C - Create (one)
@app.route('/products', methods=['POST'])
def create_product():
    # Parse the incoming JSON body to a dict
    data = ProductSchema().load(request.json)
    # Create a new instance
    new_product = Product(
        name = data['name'],
        description = data['description'],
        price = data['price'],
        stock = data['stock']
    )
    # Add to db session
    db.session.add(new_product)
    # Commit to the db
    db.session.commit()
    # Return the new product
    return ProductSchema().dump(new_product)


@app.cli.command('init_db')
def init_db():
    db.drop_all()
    db.create_all()
    print('Created tables')

@app.cli.command('seed_db')
def seed_db():
    products = [
        Product(
            name='Product 1',
            description='This is a new product',
            price=12.99,
            stock=15
        ),
        Product(
            name='Product 2',
            description='Second product',
            price=49.95,
            stock=10
        )
    ]

    # db.delete(Product)
    db.session.add_all(products)

    db.session.commit()

    print('DB Seeded')
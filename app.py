from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# DB connection string
# <protocol>://<user>:<pass>@<host>:<port>/<db_name>
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://orm_dev:123456@localhost:5432/orm_db'

db = SQLAlchemy(app)

# Model
# This just declares and configures the model in memory - the physical DB is unaffected.
class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float(precision=2))
    stock = db.Column(db.Integer, db.CheckConstraint('stock >= 0'))    

@app.route('/')
def home():
    return 'Hello!'

@app.route('/products')
def get_all_products():
    # Generate a statement
    # SELECT * FROM products;
    stmt = db.select(Product)
    # Execute the statement
    products = db.session.scalars(stmt)
    return list(products)


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
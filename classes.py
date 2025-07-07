from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from werkzeug.security import check_password_hash
import os
from flask_login import UserMixin, LoginManager

app = Flask(__name__)
app.secret_key = 'raissa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

with app.app_context():

    db.create_all()

@login_manager.user_loader
def load_user(id):
    return user.query.get(int(id))


class user(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)
    cart = db.relationship('CartItem', backref='user', cascade="all, delete-orphan", lazy=True)

    
    def verificar_senha(self, senha):
        return check_password_hash(self.senha, senha)
        
class product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    preco = db.Column(db.String(100), nullable = False)
    descricao = db.Column(db.String(200))
    product_type =  db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255))
        
class Order(db.Model):
    __tablename__ = 'Order'
    id = db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(100), nullable=False)
    
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    pedido = db.relationship('Order')
    produto = db.relationship('product')

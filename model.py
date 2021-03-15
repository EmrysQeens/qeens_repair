from flask_sqlalchemy import SQLAlchemy

db: SQLAlchemy = SQLAlchemy()
bck = SQLAlchemy()

cookie_len = 50


class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(35), nullable=False, unique=False)
    last_name = db.Column(db.String(35), nullable=False, unique=False)
    image = db.Column(db.Text, nullable=True)
    mobile_number = db.Column(db.Integer, nullable=False, unique=True)
    repairs = db.relationship('Repair', backref='customer_repairs', lazy=True)


class Repair(db.Model):
    __tablename__ = 'repairs'
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    manufacturer = db.Column(db.Integer, db.ForeignKey('manufacturers.id'), nullable=False)
    model = db.Column(db.String(25), nullable=False)
    device_pass = db.Column(db.String(30), nullable=True)
    accessories_collected = db.Column(db.String(1024), nullable=True)
    imei = db.Column(db.Integer, db.ForeignKey('imeis.id'), nullable=True)
    fault = db.Column(db.String(255), nullable=True)
    battery_serial_no = db.Column(db.String(50), nullable=True)
    cost = db.Column(db.Integer, nullable=True)
    paid = db.Column(db.Integer, nullable=True)
    balance = db.Column(db.Integer(), nullable=True)
    date_b = db.Column(db.String(40), nullable=False)
    date_c = db.Column(db.String(40), nullable=True)
    registerer = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    deliverer = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)


class Imei(db.Model):
    __tablename__ = 'imeis'
    id = db.Column(db.Integer, primary_key=True)
    imei = db.Column(db.String(15), nullable=True, unique=True)
    repairs = db.relationship('Repair', backref='imei_repairs', lazy=True)


class Manufacturer(db.Model):
    __tablename__ = 'manufacturers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    repairs = db.relationship('Repair', backref='manufacturer_repairs', lazy=True)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    image = db.Column(db.Text, nullable=True)
    is_super_user = db.Column(db.Boolean, nullable=False, default=False)


class Cookie(db.Model):
    __tablename__ = 'cookies'
    id = db.Column(db.Integer,primary_key=True)
    ip_address = db.Column(db.String(20), nullable=False, unique=True)
    cookie = db.Column(db.String(cookie_len), nullable=False, unique=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


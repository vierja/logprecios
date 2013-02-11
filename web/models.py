from datetime import datetime
from trackerapp import db
from tracker.tracker import get_parser
from urlparse import urlparse

######### MODELS

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Brand('%s')>" % self.name

class ProductCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<ProductCategory('%s')>" % self.name

class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    domain = db.Column(db.String, unique=True)

    def __init__(self, domain=None):
        self.domain = domain

    def __repr__(self):
        return "<Source('%s')>" % self.domain

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    url = db.Column(db.String, unique=True)
    pub_date = db.Column(db.DateTime)
    product_category_id = db.Column(db.Integer,
                                    db.ForeignKey('product_category.id'))
    product_category = db.relationship('ProductCategory', backref=db.backref('products', order_by=id))
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'))
    brand = db.relationship('Brand', backref=db.backref('products', order_by=id))

    source_id = db.Column(db.Integer, db.ForeignKey('source.id'))
    source = db.relationship('Source', backref=db.backref('products', order_by=id))

    original_img = db.Column(db.String)

    def __init__(self, url=None):
        self.url = url
        self.pub_date = datetime.utcnow()

    def __repr__(self):
        return "<Product('%s', '%s')>" % (self.name, self.url)

    def get_data(self):
        parser = get_parser(self.url)
        data = parser.get_data()
        self.name = data['name']
        self.original_img = data['image_url']

        #Busco o creo source
        hostname = urlparse(self.url).hostname
        if hostname.startswith('www.'):
            hostname = hostname[4:]

        source = Source.query.filter_by(domain=hostname).first()
        if source == None:
            source = Source(domain=hostname)
            db.session.add(source) #el commit se hace cuando se guarda Product.
        self.source = source

    def get_price(self):
        parser = get_parser(self.url)
        return parser.get_price()

class PriceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Numeric)
    currency = db.Column(db.String)
    fetched_date = db.Column(db.DateTime)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product', backref=db.backref('price_logs', order_by=id))

    def __init__(self, price=None, currency=None, product=None):
        self.price = price
        self.currency = currency
        self.fetched_date = datetime.utcnow()
        self.product = product

    def __repr__(self):
        return "<PriceLog('%s', '%s')>" % (self.product.name, self.price)


# def ShoppingCart(db.Model):
#     id = db.Column(db.Integer, primary_key=True)


class Paste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('paste.id'))
    parent = db.relationship('Paste', lazy=True, backref='children',
                             uselist=False, remote_side=[id])

    def __init__(self, user, code, parent=None):
        self.user = user
        self.code = code
        self.pub_date = datetime.utcnow()
        self.parent = parent


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(120))
    fb_id = db.Column(db.String(30), unique=True)
    pastes = db.relationship(Paste, lazy='dynamic', backref='user')
from datetime import datetime, date, timedelta
from trackerapp import db
from tracker.tracker import get_parser
from urlparse import urlparse
import json
from utils import slugify, DateTimeJSONEncoder

######### MODELS

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return u"<Brand('%s')>" % self.name

class ProductCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    slug = db.Column(db.String, unique=True)

    def __init__(self, name):
        self.name = name
        self.slug = slugify(name)

    def __repr__(self):
        return u"<ProductCategory('%s', '%d')>" % (self.name, self.id)

class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    domain = db.Column(db.String, unique=True)

    def __init__(self, domain=None):
        self.domain = domain

    def __repr__(self):
        return u"<Source('%s')>" % self.domain

product_categories = db.Table('product_categories',
    db.Column('product_id', db.Integer, db.ForeignKey('product_category.id')),
    db.Column('product_category_id', db.Integer, db.ForeignKey('product.id'))
)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    url = db.Column(db.String, unique=True)
    pub_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'))
    brand = db.relationship('Brand', backref=db.backref('products', order_by=id), lazy="joined", join_depth=2)

    source_id = db.Column(db.Integer, db.ForeignKey('source.id'))
    source = db.relationship('Source', backref=db.backref('products', order_by=id), lazy="joined", join_depth=2)

    product_categories = db.relationship('ProductCategory', secondary=product_categories, 
                                    backref=db.backref('products', lazy='dynamic'))

    original_img = db.Column(db.String)

    #Stats
    one_month_change = db.Column(db.Numeric(7,2))
    three_month_change = db.Column(db.Numeric(7,2))
    six_month_change = db.Column(db.Numeric(7,2))
    one_year_change = db.Column(db.Numeric(7,2))


    def __init__(self, url=None, pub_date=None):
        self.url = url
        if pub_date:
            self.pub_date = pub_date
        else:
            self.pub_date = datetime.utcnow()
        self.updated_date = datetime.utcnow()

    def __repr__(self):
        return u"<Product('%s', '%s')>" % (self.name, self.url)

    def get_data(self):
        parser = get_parser(self.url)
        data = parser.get_data()
        self.name = data['name']
        self.original_img = data['image_url']

        #Creo las categorias si no existen.
        categories = []
        for category_name in data['categories']:
            category = ProductCategory.query.filter_by(slug=slugify(category_name)).first()
            if category is None:
                category = ProductCategory(name=category_name)
            categories += [category]

        self.product_categories = categories

        #Busco o creo source
        hostname = urlparse(self.url).hostname
        if hostname.startswith('www.'):
            hostname = hostname[4:]

        source = Source.query.filter_by(domain=hostname).first()
        if source == None:
            source = Source(domain=hostname)
            db.session.add(source) #el commit se hace cuando se guarda Product.
        self.source = source
        self.updated_date = datetime.utcnow()

    def get_price(self):
        parser = get_parser(self.url)
        return parser.get_price()

    def _get_change(self, to_date=None, from_date=None, from_log=None):
        if from_log is None:
            if from_date is None:
                from_log = PriceLog.query.filter_by(product=self).order_by(db.desc(PriceLog.fetched_date)).first()
            else:
                from_log = PriceLog.query.filter_by(product=self).filter(PriceLog.fetched_date.between(from_date, from_date + timedelta(days=1))).first()

        to_log = PriceLog.query.filter_by(product=self).filter(PriceLog.fetched_date.between(to_date, to_date + timedelta(days=1))).first()
        if from_log is None or to_log is None: return 0
        return (from_log.price - to_log.price)/to_log.price * 100

    def update_stats(self, from_log=None):

        if from_log is None:
            from_log = PriceLog.query.filter_by(product=self).order_by(db.desc(PriceLog.fetched_date)).first()
        self.one_month_change = self._get_change(to_date=date.today() - timedelta(days=30), from_log=from_log)
        self.three_month_change = self._get_change(to_date=date.today() - timedelta(days=90), from_log=from_log)
        self.six_month_change = self._get_change(to_date=date.today() - timedelta(days=180), from_log=from_log)
        self.one_year_change = self._get_change(to_date=date.today() - timedelta(days=365), from_log=from_log)
        
        self.updated_date = datetime.utcnow()

    @property
    def last_3_month_change(self):
        return self._get_change(to_date=date.today() - timedelta(days=90))

    @property
    def last_year_change(self):
        return self._get_change(to_date=date.today() - timedelta(days=365.242))

    @property
    def last_month_change(self):
        return self._get_change(to_date=date.today() - timedelta(days=30))

    def to_csv_generator(self):
        csv = ""
        csv += ','.join(['ID', 'PRICE', 'CURRENCY', 'FETCHED DATE', 'CHANGE', 'PRODUCT ID', 'URL']) + '\n'
        for price_log in self.price_logs:
             csv += ','.join([str(price_log.id), "{:.2f}".format(float(price_log.price)), price_log.currency, str(price_log.fetched_date), "{:.2f}%".format(float(price_log.change)), str(self.id), self.url]) + '\n'

        return csv

    def to_json(self):
        js = {
            "id": self.id,
            "name": self.name,
            "created_time": str(self.pub_date),
            "source": {
                "id": self.source.id,
                "domain": self.source.domain 
            },
            "price_logs":{
                "data": [
                    {"id": log.id,
                     "amount": "{:.2f}".format(float(log.price)),
                     "currency":log.currency,
                     "change": "{:.2f}%".format(float(log.change)),
                     "fetched_time": str(log.fetched_date)
                    }
                        for log in self.price_logs
                ]
            } 
        }
        return json.dumps(js)

    def price_logs_to_json(self):
        price_logs = [
            [   
                log.fetched_date,
                float(log.price)
            ]
                for log in self.price_logs[::-1]
        ]
        return DateTimeJSONEncoder().encode(price_logs)

class PriceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Numeric(7,2))
    currency = db.Column(db.String)
    fetched_date = db.Column(db.DateTime)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product', backref=db.backref('price_logs', order_by=fetched_date.desc(), lazy='subquery'))
    change = db.Column(db.Numeric(7,2))

    def __init__(self, price=None, currency=None, product=None, fetched_date=None):
        previous_log = PriceLog.query.filter_by(product=product).order_by(db.desc(PriceLog.fetched_date)).limit(1).all()
        
        if previous_log:
            previous_log = previous_log[0]
            self.change = ((price - previous_log.price) / previous_log.price) * 100
        else:
            self.change = 0
        self.price = price
        self.currency = currency
        self.product = product
        if fetched_date:
            self.fetched_date = fetched_date
        else:
            self.fetched_date = datetime.utcnow()
        #Actualizo los valores.
        product.update_stats(from_log=self)


    def __repr__(self):
        return u"<PriceLog('%s', '%s')>" % (self.product.name, self.price)


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
from flask import Flask, request, url_for, redirect, \
     abort, render_template, Response
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.oauth import OAuth
from rq import use_connection
from rq_scheduler import Scheduler
from datetime import datetime
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)
oauth = OAuth()
use_connection()  # Use RQ's default Redis connection
scheduler = Scheduler()
toolbar = DebugToolbarExtension(app)


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page

from jobs.price_job import update_price
from models import Product, ProductCategory, PriceLog, Source

######### VIEWS


@app.route('/')
def homepage():
    products = Product.query.order_by(db.desc(Product.updated_date)).limit(25).all()
    number_of_logs = PriceLog.query.count()
    number_of_products = Product.query.count()
    categories = ProductCategory.query.limit(15).all()
    return render_template('home.html', products=products, number_of_logs=number_of_logs, number_of_products=number_of_products, categories=categories)


@app.route('/new-product/', methods=['GET', 'POST'])
def new_product():
    if request.method == 'POST' and request.form['url']:
        product = Product(request.form['url'])
        product.get_data()
        db.session.add(product)
        db.session.commit()
        scheduler.schedule(
            scheduled_time=datetime.now(),
            func=update_price,
            args=(product.id,),
            kwargs=None,
            interval=86400,          # One day - Time before the function is called again, in seconds
            repeat=None,             # Repeat this number of times (None means repeat forever)
            result_ttl=86400         # Se guardan los resultados 1 dia.
        )

        return redirect(url_for('show_product', product_id=product.id))
    return render_template('new_product.html')


@app.route('/product/<int:product_id>', defaults={'extension': None})
@app.route('/product/<int:product_id>.<extension>')
def show_product(product_id, extension=None):
    product = Product.query.get_or_404(product_id)
    if extension is None:
        return render_template('show_product.html', product=product)
    if extension == "json":
        return Response(product.to_json(),  mimetype='application/json')
    if extension == "csv":
        return Response(product.to_csv_generator(),  mimetype='text/csv')

    return redirect(url_for('show_product', product_id=product_id, extension=None))


@app.route('/product/<int:product_id>/price_logs.json')
def get_price_logs(product_id):
    product = Product.query.get_or_404(product_id)
    return Response(product.price_logs_to_json(), mimetype='application/json')


@app.route('/category/<category_slug>')
def show_category(category_slug):
    category = ProductCategory.query.filter_by(slug=category_slug).first()
    if category is None:
        return abort(404)

    print category
    return render_template('show_category.html', category=category)

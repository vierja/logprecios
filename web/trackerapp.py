from flask import Flask, request, url_for, redirect, flash, \
     abort, session, g, render_template, Response
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.oauth import OAuth
from rq import use_connection
from rq_scheduler import Scheduler
from datetime import datetime
from flask_debugtoolbar import DebugToolbarExtension
from tracker.tracker import get_parser

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)
oauth = OAuth()
use_connection()  # Use RQ's default Redis connection
scheduler = Scheduler()
toolbar = DebugToolbarExtension(app)


facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=app.config.get("FB_CONSUMER_KEY"),
    consumer_secret=app.config.get("FB_CONSUMER_SECRET"),
    request_token_params={'scope': 'email'}
)


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page

from jobs.price_job import update_price
from models import Product, ProductCategory, PriceLog, Source, User

######### VIEWS


@app.route('/')
def homepage():
    products = Product.query.order_by(db.desc(Product.updated_date)).limit(25).all()
    number_of_logs = PriceLog.query.count()
    number_of_products = Product.query.count()
    categories = ProductCategory.query.limit(15).all()
    return render_template('home.html', products=products, number_of_logs=number_of_logs, number_of_products=number_of_products, categories=categories)


@app.route('/stats')
def stats():
    avg_logs_by_domain = db.session.execute('''
        SELECT date_trunc('day', fetched_date) AS "day" , count(*) AS "updates", domain as "source", trim(to_char(avg(change),'99999999999999999D99')) as "avg_change"
        FROM price_log, product, source
        WHERE product_id = product.id and source_id = source.id
        GROUP BY 1,3
        ORDER BY 1;''')

    avg_changes_logs_by_domain = db.session.execute('''
        SELECT date_trunc('day', fetched_date) AS "day" , count(*) AS "updates", domain as "source", trim(to_char(avg(change),'99999999999999999D99')) as "avg_change"
        FROM price_log, product, source
        WHERE product_id = product.id and source_id = source.id AND change <> 0
        GROUP BY 1,3
        ORDER BY 1;''')
    return render_template('stats.html', avg_logs_by_domain=avg_logs_by_domain, avg_changes_logs_by_domain=avg_changes_logs_by_domain)


@app.route('/new-product/', methods=['GET', 'POST'])
def new_product():
    if request.method == 'POST' and request.form['url']:

        parser = get_parser(request.form['url'])
        if parser is None:
            return abort(400)

        url = parser.minify_url()
        product = Product.query.filter_by(url=url).first()
        if product:
            #add flash message.
            return render_template('new_product.html')

        try:
            product = Product(url, parser=parser)
            db.session.add(product)
            db.session.commit()
            scheduler.schedule(
                scheduled_time=datetime.now(),
                func=update_price,
                args=(product.id,),
                kwargs={"save_html_route": "prices_html"},
                interval=86400,          # One day - Time before the function is called again, in seconds
                repeat=None,             # Repeat this number of times (None means repeat forever)
                result_ttl=86400         # Se guardan los resultados 1 dia.
            )

            return redirect(url_for('show_product', product_id=product.id))
        except ValueError:
            abort(400)

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


@app.route('/product/<int:product_id>/price_logs.chart')
def get_price_logs_chart(product_id):
    product = Product.query.get_or_404(product_id)
    return Response(product.price_logs_to_chart(), mimetype='application/json')


@app.route('/category/<category_slug>')
def show_category(category_slug):
    category = ProductCategory.query.filter_by(slug=category_slug).first()
    if category is None:
        return abort(404)

    print category
    return render_template('show_category.html', category=category)

#### ADMIN
@app.route('/admin')
def admin():
    pass

@app.route('/admin/price_log_errors')
def price_log_errors():
    user = g.user
    if not user.is_admin:
        return abort(400)

    


#### LOGIN
@app.before_request
def check_user_status():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))


@app.route('/logout')
def logout():
    session.clear()
    flash('You were logged out')
    return redirect(url_for('homepage'))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('homepage')
    if resp is None:
        flash('You denied the login')
        return redirect(next_url)

    session['fb_access_token'] = (resp['access_token'], '')

    me = facebook.get('/me')
    user = User.query.filter_by(fb_id=me.data['id']).first()
    if user is None:
        user = User()
        user.fb_id = me.data['id']
        db.session.add(user)

    user.display_name = me.data['name']
    db.session.commit()
    session['user_id'] = user.id

    flash('You are now logged in as %s' % user.display_name)
    return redirect(next_url)


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('fb_access_token')

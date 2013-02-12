from flask import Flask, request, url_for, redirect, g, session, flash, \
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
use_connection() # Use RQ's default Redis connection
scheduler = Scheduler()
#toolbar = DebugToolbarExtension(app)

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key='188477911223606',
    consumer_secret='621413ddea2bcc5b2e83d42fc40495de',
    request_token_params={'scope': 'email'}
)

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page

from jobs.price_job import update_price
from models import Product, User, Paste, ProductCategory, PriceLog

######### VIEWS

@app.route('/')
def homepage():
    products = Product.query.order_by(db.desc(Product.updated_date)).limit(25).all()
    number_of_logs = PriceLog.query.count()
    number_of_products = Product.query.count()
    return render_template('home.html', products=products, number_of_logs=number_of_logs, number_of_products=number_of_products)

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
            interval=60,  # Time before the function is called again, in seconds
            repeat=None   # Repeat this number of times (None means repeat forever)
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


# @app.route('/', methods=['GET', 'POST'])
# def new_paste():
#     parent = None
#     reply_to = request.args.get('reply_to', type=int)
#     if reply_to is not None:
#         parent = Paste.query.get(reply_to)
#     if request.method == 'POST' and request.form['code']:
#         paste = Paste(g.user, request.form['code'], parent=parent)
#         db.session.add(paste)
#         db.session.commit()
#         return redirect(url_for('show_paste', paste_id=paste.id))
#     return render_template('new_paste.html', parent=parent)




@app.route('/<int:paste_id>')
def show_paste(paste_id):
    paste = Paste.query.options(db.eagerload('children')).get_or_404(paste_id)
    return render_template('show_paste.html', paste=paste)


@app.route('/<int:paste_id>/delete', methods=['GET', 'POST'])
def delete_paste(paste_id):
    paste = Paste.query.get_or_404(paste_id)
    if g.user is None or g.user != paste.user:
        abort(401)
    if request.method == 'POST':
        if 'yes' in request.form:
            db.session.delete(paste)
            db.session.commit()
            flash('Paste was deleted')
            return redirect(url_for('new_paste'))
        else:
            return redirect(url_for('show_paste', paste_id=paste.id))
    return render_template('delete_paste.html', paste=paste)


@app.route('/my-pastes/', defaults={'page': 1})
@app.route('/my-pastes/page/<int:page>')
def my_pastes(page):
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    pagination = Paste.query.filter_by(user=g.user).paginate(page)
    return render_template('my_pastes.html', pagination=pagination)


@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))


@app.route('/logout')
def logout():
    session.clear()
    flash('You were logged out')
    return redirect(url_for('new_paste'))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('new_paste')
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

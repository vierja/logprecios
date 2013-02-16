# -*- coding: utf8 -*-
from models import Product, Source
from trackerapp import db, scheduler, update_price
from datetime import datetime


def create_products_with_prices():
    print "Creating sources"
    source = Source(domain="tinglesa.com.uy")
    db.session.add(source)
    source = Source(domain="devoto.com.uy")
    db.session.add(source)
    source = Source(domain="multiahorro.com.uy")
    db.session.add(source)
    db.session.commit()

    print "Creating products with prices."
    #Tienda inglesa
    tienda_inglesa_urls = [
        'http://www.tinglesa.com.uy/producto.php?idarticulo=9974',
        'http://www.tinglesa.com.uy/producto.php?idarticulo=9578',
        'http://www.tinglesa.com.uy/producto.php?idarticulo=219091',
        'http://www.tinglesa.com.uy/producto.php?idarticulo=5478',
        'http://www.tinglesa.com.uy/producto.php?idarticulo=8764',
        'http://www.tinglesa.com.uy/producto.php?idarticulo=1849',
        'http://www.tinglesa.com.uy/producto.php?idarticulo=1788',
        'http://www.tinglesa.com.uy/producto.php?idarticulo=5994',
        'http://www.tinglesa.com.uy/producto.php?idarticulo=1151',
        'http://www.tinglesa.com.uy/producto.php?idarticulo=6008',
        'http://www.tinglesa.com.uy/producto.php?idarticulo=6185',
        'http://www.tinglesa.com.uy/producto.php?idarticulo=6004',
        'http://www.tinglesa.com.uy/producto.php?idarticulo=6280',
        'http://www.tinglesa.com.uy/producto.php?idarticulo=23125',
        'http://www.tinglesa.com.uy/producto.php?idarticulo=212',
        'http://www.tinglesa.com.uy/producto.php?idarticulo=1026'
    ]

    #Devoto
    devoto_urls = [
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,4253,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,4254,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,4249,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,4250,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,5132,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,48552,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,4909,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,4910,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,126854,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,4256,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,126918,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,126862,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,126917,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,126861,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,132213,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,4245,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,4244,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,141235,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,14026,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,6925,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,6926,0,274,1',
        'http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,5744,0,274,1'
    ]

    multiahorro = [
        'http://www.multiahorro.com.uy/Product.aspx?p=168548',
        'http://www.multiahorro.com.uy/Product.aspx?p=118216',
        'http://www.multiahorro.com.uy/Product.aspx?p=118223',
        'http://www.multiahorro.com.uy/Product.aspx?p=118230',
        'http://www.multiahorro.com.uy/Product.aspx?p=163355',
        'http://www.multiahorro.com.uy/Product.aspx?p=163359',
        'http://www.multiahorro.com.uy/Product.aspx?p=163366',
        'http://www.multiahorro.com.uy/Product.aspx?p=163367',
        'http://www.multiahorro.com.uy/Product.aspx?p=134130',
        'http://www.multiahorro.com.uy/Product.aspx?p=118224',
        'http://www.multiahorro.com.uy/Product.aspx?p=176558',
        'http://www.multiahorro.com.uy/Product.aspx?p=176554',
        'http://www.multiahorro.com.uy/Product.aspx?p=118225',
        'http://www.multiahorro.com.uy/Product.aspx?p=100826',
        'http://www.multiahorro.com.uy/Product.aspx?p=178870',
        'http://www.multiahorro.com.uy/Product.aspx?p=193131',
        'http://www.multiahorro.com.uy/Product.aspx?p=193132',
        'http://www.multiahorro.com.uy/Product.aspx?p=100774',
        'http://www.multiahorro.com.uy/Product.aspx?p=100773',
        'http://www.multiahorro.com.uy/Product.aspx?p=100771',
        'http://www.multiahorro.com.uy/Product.aspx?p=100768',
        'http://www.multiahorro.com.uy/Product.aspx?p=100770',
        'http://www.multiahorro.com.uy/Product.aspx?p=193197',
        'http://www.multiahorro.com.uy/Product.aspx?p=176686',
        'http://www.multiahorro.com.uy/Product.aspx?p=167302',
        'http://www.multiahorro.com.uy/Product.aspx?p=167299',
        'http://www.multiahorro.com.uy/Product.aspx?p=167307',
        'http://www.multiahorro.com.uy/Product.aspx?p=118218',
        'http://www.multiahorro.com.uy/Product.aspx?p=118220',
        'http://www.multiahorro.com.uy/Product.aspx?p=143160',
        'http://www.multiahorro.com.uy/Product.aspx?p=193124',
        'http://www.multiahorro.com.uy/Product.aspx?p=193123',
        'http://www.multiahorro.com.uy/Product.aspx?p=193126',
        'http://www.multiahorro.com.uy/Product.aspx?p=193125',
        'http://www.multiahorro.com.uy/Product.aspx?p=176606',
        'http://www.multiahorro.com.uy/Product.aspx?p=176586',
        'http://www.multiahorro.com.uy/Product.aspx?p=176610',
        'http://www.multiahorro.com.uy/Product.aspx?p=176663',
        'http://www.multiahorro.com.uy/Product.aspx?p=176664',
        'http://www.multiahorro.com.uy/Product.aspx?p=176684',
        'http://www.multiahorro.com.uy/Product.aspx?p=176685',
        'http://www.multiahorro.com.uy/Product.aspx?p=176687',
        'http://www.multiahorro.com.uy/Product.aspx?p=176609',
        'http://www.multiahorro.com.uy/Product.aspx?p=176682',
        'http://www.multiahorro.com.uy/Product.aspx?p=176683',
        'http://www.multiahorro.com.uy/Product.aspx?p=100720',
        'http://www.multiahorro.com.uy/Product.aspx?p=100719',
        'http://www.multiahorro.com.uy/Product.aspx?p=118229',
        'http://www.multiahorro.com.uy/Product.aspx?p=100711',
        'http://www.multiahorro.com.uy/Product.aspx?p=143614',
        'http://www.multiahorro.com.uy/Product.aspx?p=143636',
        'http://www.multiahorro.com.uy/Product.aspx?p=171686',
        'http://www.multiahorro.com.uy/Product.aspx?p=143292',
        'http://www.multiahorro.com.uy/Product.aspx?p=143598',
        'http://www.multiahorro.com.uy/Product.aspx?p=167306',
        'http://www.multiahorro.com.uy/Product.aspx?p=167300',
        'http://www.multiahorro.com.uy/Product.aspx?p=118222',
        'http://www.multiahorro.com.uy/Product.aspx?p=118227',
        'http://www.multiahorro.com.uy/Product.aspx?p=176582',
        'http://www.multiahorro.com.uy/Product.aspx?p=176587',
    ]

    list_of_lists = [multiahorro, devoto_urls, tienda_inglesa_urls]

    for url_list in list_of_lists:
        for url in url_list:
            product = Product(url)
            product.get_data()
            db.session.add(product)
            db.session.commit()
            scheduler.schedule(
                scheduled_time=datetime.now(),
                func=update_price,
                args=(product.id,),
                kwargs=None,
                interval=86400, #One day # Time before the function is called again, in seconds
                repeat=None              # Repeat this number of times (None means repeat forever)
            )

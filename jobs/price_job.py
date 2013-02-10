import sys
import traceback

def update_price(product_id, product_currency='UYP', recursion_limit=0):
    if recursion_limit > 5:
        raise Exception("Recursion limit.")

    #Importo aca adentro para no tener problema con imports circulares.
    from web.trackerapp import db
    from web.models import Product, PriceLog
    try:
        product = Product.query.get(product_id)
        new_price = product.get_price()
        price_log = PriceLog(new_price, product_currency, product)
        db.session.add(price_log)
        db.session.commit()
    except:
        exc_string = ''.join(
                traceback.format_exception_only(*sys.exc_info()[:2]) +
                traceback.format_exception(*sys.exc_info()))
        print exc_string
        #Llamo para probar otra vez.
        update_price(product_id, recursion_limit=recursion_limit+1)
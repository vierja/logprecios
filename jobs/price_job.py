import time
import requests
from tracker.tracker import get_parser
from rq import get_current_job
from datetime import datetime
import os


def update_price(product_id, product_currency='UYP', save_html_route='prices_html', recursion_limit=0, e=None):

    if recursion_limit > 5:
        raise e

    job = get_current_job()
    job.meta['product_id'] = product_id
    job.save()

    #Importo aca adentro para no tener problema con imports circulares.
    from web.trackerapp import db
    from web.models import Product, PriceLog, PriceLogError
    try:
        product = Product.query.get(product_id)
        result = requests.get(product.url, timeout=30, allow_redirects=False)

        if result.status_code == 302:
            price_log_error = PriceLogError(product, job.id)
            price_log_error.message = "Product URL is redirected with %d." % (result.status_code)
            db.session.add(price_log_error)
            db.session.commit()
            return False

        if result.status_code >= 300:
            #Error en la pagina que no es el de temporalmente inhabilitado.
            price_log_error = PriceLogError(product, job.id)
            price_log_error.message = "Product URL returns wrong status code: %d." % (result.status_code)
            db.session.add(price_log_error)
            db.session.commit()
            return False

        parser = get_parser(product.url)
        product_data = parser.get_data(result.text)

        if product_data['name'] != product.name:
            price_log_error = PriceLogError(product, job.id)
            price_log_error.message = "Product Name differs from original. Original: %s, New: %s" % (product.name, product_data['name'])
            db.session.add(price_log_error)
            db.session.commit()
            return False

        if product_data['image_url'] != product.original_img:
            # Si la URL de la imagen cambio entonces la actualizo.
            product.original_img = product_data['image_url']
            db.session.add(product)

        new_price = product_data['price']
        price_log = PriceLog(new_price, product_currency, product)

        """
        Si se quiere guardar un archivo entonces se guardan los datos en un .gz
        y se guarda el nombre del archivo en la tabla.
        """
        try:
            import gzip
            now = datetime.utcnow()
            folder_path = "%s/%s" % (os.path.abspath(save_html_route), now.strftime("%Y-%m-%d"))
            if not os.path.isdir(folder_path):
                os.mkdir(folder_path)
            file_name = "product_%d-%s.html.gz" % (product.id, now.strftime("%H_%M_%S"))
            f = gzip.open("%s/%s" % (folder_path, file_name), 'wb')
            f.write(result.content)
            f.close()
            price_log.html_file_name = file_name
        except:
            job.meta['error'] = 'Error while saving gz.'
            job.save()

        db.session.add(price_log)
        db.session.commit()

    except requests.exceptions.Timeout, ex:
        #Llamo para probar otra vez.
        #Server down or overloaded.
        time.sleep(60)
        update_price(product_id, recursion_limit=recursion_limit + 1, e=ex)

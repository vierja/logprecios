from rq import Queue, use_connection
from jobs.price_job import update_price


def schedule_jobs(interval):
    from web.trackerapp import db
    from web.trackerapp import Product
    products_id_to_fetch = db.session.execute("""(SELECT product.id as id
        FROM product
        LEFT JOIN price_log ON (price_log.product_id = product.id)
        LEFT JOIN price_log_error ON (price_log_error.product_id = product.id)
        WHERE
        (
            -- Si le restamos X secondos a la hora y queda mayor, quiere decir que se pasa a la hora del dia despues.
            -- en esta parte de la query, solo buscamos los resultados del dia de ayer
            -- es decir que la fecha de publicacion sean mas grande que la resta.
            (now()::time  - interval '%d seconds')::time > now()::time
            AND
            tracking_time::time > (now()::time  - interval '%d seconds')::time
        )
        GROUP BY 1
        -- a estos casos chequeamos que lo ultimo encontrado ya sea precio o error sea menor que el dia de ayer (dia cuando se deberia de haber buscado el precio)
        HAVING (MAX(price_log.fetched_date) IS NULL OR date_trunc('day', MAX(price_log.fetched_date)) < date_trunc('day',  now() - interval '1 day')) AND
        (MAX(price_log_error.error_date) IS NULL OR date_trunc('day', MAX(price_log_error.error_date)) < date_trunc('day',  now()  - interval '1 day')))
        UNION
        (SELECT product.id as id
        FROM product
        LEFT JOIN price_log ON (price_log.product_id = product.id)
        LEFT JOIN price_log_error ON (price_log_error.product_id = product.id)
        WHERE
        (
            -- Analogamente que arriba, en esta parte buscamos los resultados del dia de hoy.
            -- es decir que la hora sea menor que la hora actual.
            (now()::time  - interval '%d seconds')::time > now()::time
            AND
            tracking_time::time < now()::time
        ) OR (NOT (now()::time  - interval '%d seconds')::time > now()::time
            -- O, si no cambiamos de dia restando el interval entonces buscamos dentro del intervalo.
            AND
            (
                tracking_time::time > (now()::time  - interval '%d seconds')::time
                AND
                tracking_time::time < now()::time
            )
        )
        GROUP BY 1
        -- en estos casos chequeamos que el ultimo precio no sea del dia de hoy
        HAVING (MAX(price_log.fetched_date) IS NULL OR date_trunc('day', MAX(price_log.fetched_date)) < date_trunc('day',  now())) AND
        (MAX(price_log_error.error_date) IS NULL OR date_trunc('day', MAX(price_log_error.error_date)) < date_trunc('day',  now())));""" % (interval, interval, interval, interval, interval))

    list_of_ids = []
    for row in products_id_to_fetch:
        list_of_ids += [row['id']]

    if len(list_of_ids) == 0:
        return True

    products_to_fetch = Product.query.filter(Product.id.in_(list_of_ids))

    use_connection()
    q = Queue()

    for product in products_to_fetch:
        print product.id
        q.enqueue(update_price, args=(product.id,), kwargs={"save_html_route": "prices_html"})

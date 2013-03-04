from datetime import datetime, timedelta
from trackerapp import Product, db


# Tomado de http://stackoverflow.com/a/1217947/310467
def page_query(q):
    offset = 0
    while True:
        r = False
        for elem in q.limit(1000).offset(offset):
            r = True
            yield elem
        offset += 1000
        if not r:
            break


def reset_times():
    number_of_products = Product.query.count()
    second_interval = int(86400 / number_of_products)
    starting_time = datetime.utcnow()
    second_offset = 0

    for product in page_query(Product.query):
        scheduled_time = starting_time + timedelta(seconds=second_offset)
        product.tracking_time = scheduled_time
        db.session.add(product)
        print "will be schedule to:", scheduled_time
        second_offset += second_interval

    print "Number of products scheduled:", len(number_of_products)
    db.session.commit()

if __name__ == "__main__":
    reset_times()

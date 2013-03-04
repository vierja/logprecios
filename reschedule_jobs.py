from datetime import datetime, timedelta
from trackerapp import Product, db


def reset_times():

    number_of_products = Product.query.count()

    second_interval = int(86400 / number_of_products)

    starting_time = datetime.utcnow()
    second_offset = 0

    for product in Product.query.all():
        scheduled_time = starting_time + timedelta(seconds=second_offset)
        product.tracking_time = scheduled_time
        db.session.add(product)
        print "will be schedule to:", scheduled_time
        second_offset += second_interval

    print "Number of products scheduled:", len(number_of_products)
    db.session.commit()

if __name__ == "__main__":
    reset_times()

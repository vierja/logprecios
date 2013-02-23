from pyquery import PyQuery as pq
from urlparse import urlparse, urljoin
from utils import is_number, to_decimal
import re
from parser import Parser


class MultiAhorroParser(Parser):
    def __init__(self, *args, **kwargs):
        super(MultiAhorroParser, self).__init__(*args, **kwargs)
        if not self.url_is_valid():
            raise ValueError("Invalid URL")
        self.url = self.minify_url()

    def minify_url(self):
        return self.url

    def url_is_valid(self):
        #Nos aseguramos que la url sea valida
        o = urlparse(self.url)
        params = dict([a.split("=") for a in o.query.split("&")])
        return ((o.hostname == "multiahorro.com.uy" or o.hostname == "www.multiahorro.com.uy") and
                "p" in params and params["p"].isdigit())

    def get_data(self, content=None):
        if content is None:
            d = pq(url=self.url, opener=self.opener)
        else:
            d = pq(content)

        # Product name
        product_name = d("h1:first").text()
        product_name = re.sub(' +', ' ', product_name)
        # if d("#ctl00_ContentPlaceHolder1_lblUnitType").text().lower() == 'kg':
        #     product_name += " 1 Kg"
        # Product image
        incomplete_link = d("#ctl00_ContentPlaceHolder1_imgProductImage").attr("src")
        clean_link = urljoin(self.url, incomplete_link[1:])
        # Product categories
        categorias = d("#ctl00_ContentPlaceHolder1_lblMap").text().split(" -> ")[1:-1]
        # Product price
        price_with_currency = d('#ctl00_ContentPlaceHolder1_lblPrecioMA').text()
        #Precio se obtiene "$ 33.00"
        price_str = price_with_currency.strip().split(" ")[1]
        assert is_number(price_str)
        price = to_decimal(price_str)
        return {'name': product_name, "price": price, "image_url": clean_link, "categories": categorias}

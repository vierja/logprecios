from pyquery import PyQuery as pq
from urlparse import urlparse, parse_qsl, urlunparse
import urllib
from utils import is_number, to_decimal
import re
from parser import Parser


class TiendaInglesaParser(Parser):
    def __init__(self, *args, **kwargs):
        super(TiendaInglesaParser, self).__init__(*args, **kwargs)
        if not self.url_is_valid():
            raise ValueError("Invalid URL")
        self.url = self.minify_url()

    def minify_url(self):
        url_parsed = urlparse(self.url)
        #['http', 'www.tinglesa.com.uy', '/producto.php', '--path--', 'idarticulo=3148&trash=1', 'tag']
        url_list = list(url_parsed)
        #Sets fragment to empty.
        url_list[5] = ''
        query = dict(parse_qsl(url_parsed.query))
        for k in query.keys():
            if k != 'idarticulo':
                query.pop(k)
        #Sets query
        url_list[4] = urllib.urlencode(query)
        #Sets to http
        url_list[0] = 'http'
        #Sets domain with www
        if not url_list[1].startswith('www.'):
            url_list[1] = 'www.' + url_list[1]
        return urlunparse(url_list)

    def url_is_valid(self):
        o = urlparse(self.url)
        params = dict([a.split("=") for a in o.query.split("&")])
        return ((o.hostname == "tinglesa.com.uy" or o.hostname == "www.tinglesa.com.uy") and
                "idarticulo" in params and
                params["idarticulo"].isdigit())

    def get_data(self, content=None):
        if content is None:
            d = pq(url=self.url, opener=self.opener)
        else:
            d = pq(content)

        # Product name
        product_name = d(".prod:first").find("h2").text()
        # Product image
        dirty_link = d(".contenedor_foto_producto>a").attr("href")
        clean_link = re.search("\(\'(?P<url>https?://[^\s]+)\',", dirty_link).group("url")
        # Product categories
        categories = d(".btn_navegacion").find("td:nth-child(2)").find(".link_nav")[1:-1]
        categories = [d(a).text().strip() for a in categories]
        # Product price
        price_with_currency = d('.precio_producto').find("span").text()
        #Precio se obtiene "$ 33.00"
        price_str = price_with_currency.strip().split(" ")[1]
        assert is_number(price_str)
        price = to_decimal(price_str)

        return {'name': product_name, "price": price, "image_url": clean_link, "categories": categories}

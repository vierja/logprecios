from pyquery import PyQuery as pq
from urlparse import urlparse, urlunparse
from utils import is_number, to_decimal
from parser import Parser


class DevotoParser(Parser):
    def __init__(self, *args, **kwargs):
        super(DevotoParser, self).__init__(*args, **kwargs)
        if not self.url_is_valid():
            raise ValueError("Invalid URL")
        self.url = self.minify_url()

    def minify_url(self):
        url_parsed = urlparse(self.url)
        #['http', 'www.tinglesa.com.uy', '/producto.php', '--path--', 'idarticulo=3148&trash=1', 'tag']
        url_list = list(url_parsed)
        #Sets fragment to empty.
        url_list[5] = ''
        query_splitted = url_parsed.query.split("&")
        query_string = query_splitted[0]
        query_string = ','.join(query_string.split(',')[:6])
        #Sets query
        url_list[4] = query_string
        #Sets to http
        url_list[0] = 'http'
        #Sets domain with www
        if not url_list[1].startswith('www.'):
            url_list[1] = 'www.' + url_list[1]
        return urlunparse(url_list)

    def url_is_valid(self):
        #Nos aseguramos que la url sea valida
        o = urlparse(self.url)
        path = o.path.split("/")[-1]
        return ((o.hostname == "devoto.com.uy" or o.hostname == "www.devoto.com.uy") and
                path == "hdetalleproductop")

    def get_data(self, content=None):
        if content is None:
            d = pq(url=self.url, opener=self.opener)
        else:
            d = pq(content)

        # Product name
        product_name = d("h1").text()
        # Product image
        incomplete_link = d("img[class=imgproducto]").attr("src")
        clean_link = "http://" + urlparse(self.url).hostname + incomplete_link
        # Product categories
        categories = d(".barnavega").text().split("/")[1:-1]
        categories = [a.strip() for a in categories]
        # Product price
        price_with_currency = d('h1').parent().find("span").eq(1).text()
        # Precio se obtiene "$U 33.00"
        price_str = price_with_currency.strip().split(" ")[1]
        assert is_number(price_str)
        price = to_decimal(price_str)

        return {'name': product_name, "price": price, "image_url": clean_link, "categories": categories}

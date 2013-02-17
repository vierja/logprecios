from pyquery import PyQuery as pq
from urlparse import urlparse, parse_qsl, urlunparse
import urllib
from utils import is_number, to_decimal
import re
from parser import Parser


class TiendaInglesaParser(Parser):
    def __init__(self, *args, **kwargs):
        super(TiendaInglesaParser, self).__init__(*args, **kwargs)

    def minify(self):
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
        assert o.hostname == "tinglesa.com.uy" or o.hostname == "www.tinglesa.com.uy"
        params = dict([a.split("=") for a in o.query.split("&")])
        assert "idarticulo" in params
        assert params["idarticulo"].isdigit()
        hostname = o.hostname
        if hostname.startswith('www.'):
            hostname = hostname[4:]
        return hostname

    def get_data(self):
        hostname = self.url_is_valid()
        d = pq(url=self.url, opener=self.opener)
        product_name = d(".prod:first").find("h2").text()
        dirty_link = d(".contenedor_foto_producto>a").attr("href")
        clean_link = re.search("\(\'(?P<url>https?://[^\s]+)\',", dirty_link).group("url")
        #categories
        categorias = d(".btn_navegacion").find("td:nth-child(2)").find(".link_nav")[1:-1]
        categorias = [d(a).text().strip() for a in categorias]

        return {'name': product_name, "image_url": clean_link, "categories": categorias, "hostname": hostname}

    def get_price(self):
        """
        Obtiene el valor de el producto con url `url`.
        La url debe de ser del tipo
        `http://www.tinglesa.com.uy/producto.php?idarticulo=1727`
        para ser procesada.
        """
        self.url_is_valid()
        d = pq(url=self.url, opener=self.opener)
        precio_con_moneda = d('.precio_producto').find("span").text()
        #Precio se obtiene "$ 33.00"
        precio = precio_con_moneda.strip().split(" ")[1]
        assert is_number(precio)

        return to_decimal(precio)

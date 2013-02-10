from pyquery import PyQuery as pq
from urlparse import urlparse
from utils import is_number, to_decimal
import re
from parser import Parser

class TiendaInglesaParser(Parser):
    def __init__(self, *args, **kwargs):
        super(TiendaInglesaParser, self).__init__(*args, **kwargs)

    def url_is_valid(self):
        o = urlparse(self.url)
        assert o.hostname == "tinglesa.com.uy" or o.hostname == "www.tinglesa.com.uy"
        params = dict([a.split("=") for a in o.query.split("&")])
        assert "idarticulo" in params
        assert params["idarticulo"].isdigit()

    def get_data(self):
        self.url_is_valid()
        d = pq(url=self.url, opener=self.opener)
        product_name = d(".prod:first").find("h2").text()
        dirty_link = d(".contenedor_foto_producto>a").attr("href")
        clean_link = re.search("\(\'(?P<url>https?://[^\s]+)\',", dirty_link).group("url")
        return {'name':product_name, "image_url": clean_link}

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

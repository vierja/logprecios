from baseparser import BaseParser
from pyquery import PyQuery as pq
from urlparse import urlparse

class TiendaInglesaParser(BaseParser):

    def get_value(self, url):
        """
        Obtiene el valor de el producto con url `url`.
        La url debe de ser del tipo 
        `http://www.tinglesa.com.uy/producto.php?idarticulo=1727`
        para ser procesada.
        """
        #Nos aseguramos que la url sea valida
        o = urlparse(url)
        assert o.hostname == "tinglesa.com.uy" or o.hostname == "www.tinglesa.com.uy"
        params = dict([a.split("=") for a in o.query.split("&")])
        assert "idarticulo" in params
        assert params["idarticulo"].isdigit()

        d = pq(url=url)
        precio_con_moneda = d('.precio_producto').find("span").text()
        #Precio se obtiene "$ 33.00"
        precio = precio_con_moneda.strip().split(" ")[1]

        assert self.is_number(precio)

        return self.to_decimal(precio)

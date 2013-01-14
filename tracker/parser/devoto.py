from baseparser import BaseParser
from pyquery import PyQuery as pq
from urlparse import urlparse

class DevotoParser(BaseParser):

    def get_value(self, url):
        """
        Obtiene el valor de el producto con url `url`.
        La url debe de ser del tipo 
        `http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,6570,0,269,1`
        para ser procesada.
        """
        #Nos aseguramos que la url sea valida
        o = urlparse(url)
        assert o.hostname == "devoto.com.uy" or o.hostname == "www.devoto.com.uy"
        path = o.path.split("/")[-1]
        assert path == "hdetalleproductop"

        d = pq(url=url)
        precio_con_moneda = d('h1').parent().find("span").eq(1).text()
        #Precio se obtiene "$U 33.00"
        precio = precio_con_moneda.strip().split(" ")[1]

        assert self.is_number(precio)

        return self.to_decimal(precio)

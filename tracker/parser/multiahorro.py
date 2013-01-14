from baseparser import BaseParser
from pyquery import PyQuery as pq
from urlparse import urlparse

class MultiAhorroParser(BaseParser):

    def get_value(self, url):
        """
        Obtiene el valor de el producto con url `url`.
        La url debe de ser del tipo 
        `http://www.multiahorro.com.uy/Product.aspx?p=119739`
        para ser procesada.
        """
        #Nos aseguramos que la url sea valida
        o = urlparse(url)
        assert o.hostname == "multiahorro.com.uy" or o.hostname == "www.multiahorro.com.uy"
        params = dict([a.split("=") for a in o.query.split("&")])
        assert "p" in params
        assert params["p"].isdigit()

        d = pq(url=url)
        precio_con_moneda = d('#ctl00_ContentPlaceHolder1_lblPrecioMA').text()
        #Precio se obtiene "$ 33.00"
        precio = precio_con_moneda.strip().split(" ")[1]

        assert self.is_number(precio)

        return self.to_decimal(precio)

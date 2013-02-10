from pyquery import PyQuery as pq
from urlparse import urlparse, urljoin
from utils import is_number, to_decimal
import re
from parser import Parser

class MultiAhorroParser(Parser):
    def __init__(self, *args, **kwargs):
        super(MultiAhorroParser, self).__init__(*args, **kwargs)

    def url_is_valid(self):
        #Nos aseguramos que la url sea valida
        o = urlparse(self.url)
        assert o.hostname == "multiahorro.com.uy" or o.hostname == "www.multiahorro.com.uy"
        params = dict([a.split("=") for a in o.query.split("&")])
        assert "p" in params
        assert params["p"].isdigit()

    def get_data(self):
        self.url_is_valid()
        d = pq(url=self.url, opener=self.opener)
        product_name = d("h1:first").text()
        product_name = re.sub(' +',' ', product_name)
        if d("#ctl00_ContentPlaceHolder1_lblUnitType").text().lower() == 'kg':
            product_name += " 1 Kg"
        incomplete_link = d("#ctl00_ContentPlaceHolder1_imgProductImage").attr("src")
        clean_link = urljoin(self.url, incomplete_link[1:])
        return {'name':product_name, "image_url": clean_link}

    def get_price(self):
        """
        Obtiene el valor de el producto con url `url`.
        La url debe de ser del tipo 
        `http://www.multiahorro.com.uy/Product.aspx?p=119739`
        para ser procesada.
        """
        self.url_is_valid()
        d = pq(url=self.url, opener=self.opener)
        precio_con_moneda = d('#ctl00_ContentPlaceHolder1_lblPrecioMA').text()
        #Precio se obtiene "$ 33.00"
        precio = precio_con_moneda.strip().split(" ")[1]

        assert is_number(precio)

        return to_decimal(precio)

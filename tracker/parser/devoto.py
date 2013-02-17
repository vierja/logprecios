from pyquery import PyQuery as pq
from urlparse import urlparse, urlunparse
from utils import is_number, to_decimal
from parser import Parser


class DevotoParser(Parser):
    def __init__(self, *args, **kwargs):
        super(DevotoParser, self).__init__(*args, **kwargs)

    def minify(self):
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
        assert o.hostname == "devoto.com.uy" or o.hostname == "www.devoto.com.uy"
        path = o.path.split("/")[-1]
        assert path == "hdetalleproductop"
        hostname = o.hostname
        if hostname.startswith('www.'):
            hostname = hostname[4:]
        return hostname

    def get_data(self):
        hostname = self.url_is_valid()
        d = pq(url=self.url, opener=self.opener)
        product_name = d("h1").text()
        incomplete_link = d("img[class=imgproducto]").attr("src")
        clean_link = "http://" + urlparse(self.url).hostname + incomplete_link
        #Categorias
        categories = d(".barnavega").text().split("/")[1:-1]
        categories = [a.strip() for a in categories]

        return {'name': product_name, "image_url": clean_link, "categories": categories, "hostname": hostname}

    def get_price(self):
        """
        Obtiene el valor de el producto con url `url`.
        La url debe de ser del tipo
        `http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,6570,0,269,1`
        para ser procesada.
        """
        self.url_is_valid()
        d = pq(url=self.url, opener=self.opener)
        precio_con_moneda = d('h1').parent().find("span").eq(1).text()
        #Precio se obtiene "$U 33.00"
        precio = precio_con_moneda.strip().split(" ")[1]

        assert is_number(precio)

        return to_decimal(precio)

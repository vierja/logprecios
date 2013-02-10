import times
import csv
import os

from parser.devoto import DevotoParser
from parser.multiahorro import MultiAhorroParser
from parser.tiendainglesa import TiendaInglesaParser

def get_parser(url):
    if "devoto" in url.lower():
        return DevotoParser(url)
    if "tinglesa" in url.lower():
        return TiendaInglesaParser(url)
    if "multiahorro" in url.lower():
        return MultiAhorroParser(url)

    raise Exception("Invalid url. No parser found.")


class TrackerInflacion(object):
    """
    Tracker de inflacion.
    Lee de la lista de productos en el archivo data/productos.csv
    y genera una carpeta (por ej. 2013-01-14/) con un archivo precios.csv
    dentro con los precios obtenido de los productos.
    `data_folder` puede ser absoluta o relativo al root del directorio principal.
    `price_folder` debe de ser relativo desde `data_folder`
    """
    def __init__(self, data_folder="data/", product_file="productos.csv", price_folder=None, price_file_name="precios"):
        super(TrackerInflacion, self).__init__()
        self.date = times.now()
        if os.path.isabs(data_folder):
            self.data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", data_folder))
        else:
            self.data_folder = data_folder

        self.product_file = product_file
        if price_folder is None:
            #Los datos se guardan en una carpeta de el mes.
            price_folder = self.date.strftime("%Y-%m")

        self.price_folder = os.path.abspath(os.path.join(self.data_folder, price_folder)) + "/"
        self.price_file = self.date.strftime("%Y-%m-%d") + "_" + price_file_name + ".csv"
        #Creo la carpeta de data si no existe.
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

        #Creo la carpeta de captura si no existe.
        if not os.path.exists(self.price_folder):
            os.makedirs(self.price_folder)

    def get_parser(self, url):
        if "devoto" in url.lower():
            return parser.devoto.get_price
        if "tinglesa" in url.lower():
            return parser.tiendainglesa.get_price
        if "multiahorro" in url.lower():
            return parser.multiahorro.get_price

        raise Exception("Invalid url. No parser found.")

    def get_prices(self):
        product_route = self.data_folder + self.product_file
        price_route = self.price_folder + self.price_file

        with open(product_route, 'rb') as products_csv, open(price_route, 'wb') as price_csv:
            product_reader = csv.reader(products_csv, delimiter=',', quotechar='"', skipinitialspace=True)
            price_writer = csv.writer(price_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

            headers = product_reader.next()
            assert headers == ["producto", "marca", "nombre", "fuente", "categoria", "url"]
            price_writer.writerow(["producto", "marca", "fuente", "categoria", "precio", "moneda", "fecha", "error"])

            for product_row in product_reader:
                try:
                    get_price = self.get_parser(product_row[5])
                    value = get_price(product_row[5])
                    price_writer.writerow([product_row[0], product_row[1], product_row[3], product_row[4], "{0:.2f}".format(round(value,2)), "UYP", str(times.now()), ""])
                except Exception, e:
                    price_writer.writerow([product_row[0], product_row[1], product_row[3], product_row[4], "", "", str(times.now()), str(e)])


        
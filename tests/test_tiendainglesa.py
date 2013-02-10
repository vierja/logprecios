import unittest
from tracker.parser.tiendainglesa import TiendaInglesaParser

class TestTiendaInglesaParser(unittest.TestCase):

    def assertValue(self, url, value):
        parser = TiendaInglesaParser(url)
        site_value = parser.get_price()
        assert site_value == value

    def assertData(self, url, name, image_url):
        parser = TiendaInglesaParser(url)
        res = parser.get_data()
        assert res['name'] == name
        assert res['image_url'] == image_url

    def test_leche(self):
        self.assertValue("http://www.tinglesa.com.uy/producto.php?idarticulo=1531", 15.5)

    def test_leche_data(self):
        self.assertData("http://www.tinglesa.com.uy/producto.php?idarticulo=1531", "LECHE  CONAPROLE FRESCA ENTERA SACHET 1LT", "http://fotosti.e-tradeconsult.com/1200x900/VM000100/VM000161-1.jpg")

if __name__ == '__main__':
    unittest.main()
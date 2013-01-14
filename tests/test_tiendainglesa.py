import unittest
from tracker.parser.tiendainglesa import TiendaInglesaParser

class TestTiendaInglesaParser(unittest.TestCase):

    def assertValue(self, url, value):
        p = TiendaInglesaParser()
        site_value = p.get_value(url)
        assert site_value == value

    def test_leche(self):
        self.assertValue("http://www.tinglesa.com.uy/producto.php?idarticulo=1531", 15.5)

if __name__ == '__main__':
    unittest.main()
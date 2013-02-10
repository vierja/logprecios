import unittest
from tracker.parser.multiahorro import MultiAhorroParser

class TestMultiAhorroParser(unittest.TestCase):

    def assertValue(self, url, value):
        parser = MultiAhorroParser(url)
        site_value = parser.get_price()
        assert site_value == value

    def assertData(self, url, name, image_url):
        parser = MultiAhorroParser(url)
        res = parser.get_data()
        assert res['name'] == name
        assert res['image_url'] == image_url

    def test_leche_value(self):
        self.assertValue("http://www.multiahorro.com.uy/Product.aspx?p=94295", 16)

    def test_leche_data(self):
        self.assertData("http://www.multiahorro.com.uy/Product.aspx?p=94295", "LECHE CONAP. FRESCA DESCR. 1L", "http://www.multiahorro.com.uy/images/Products/small/610912.jpg")

    def test_cebolla_value(self):
        self.assertValue("http://www.multiahorro.com.uy/Product.aspx?p=106671", 36)

    def test_cebolla_data(self):
        self.assertData("http://www.multiahorro.com.uy/Product.aspx?p=106671", "CEBOLLA 1 Kg", "http://www.multiahorro.com.uy/images/Products/small/953150.jpg")

if __name__ == '__main__':
    unittest.main()
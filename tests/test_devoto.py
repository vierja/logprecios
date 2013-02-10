import unittest
from tracker.parser.devoto import DevotoParser

class TestDevotoParser(unittest.TestCase):

    def assertValue(self, url, value):
        parser = DevotoParser(url)
        site_value = parser.get_price()
        assert site_value == value

    def assertData(self, url, name, image_url):
        parser = DevotoParser(url)
        res = parser.get_data()
        assert res['name'] == name
        assert res['image_url'] == image_url

    def test_leche(self):
        self.assertValue("http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,528,0,0,1", 15.5)

    def test_leche_data(self):
        self.assertData("http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,528,0,0,1","LECHE FRESCA ENTERA CONAPROLE - SC 1 LT","http://www.devoto.com.uy/mvdcommerce/imgUpload/240501_gr.jpg")

if __name__ == '__main__':
    unittest.main()
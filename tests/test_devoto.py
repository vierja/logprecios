import unittest
from test_parser import TestParser


class TestDevotoParser(TestParser):

    def test_leche_data(self):
        self.assertData("http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,528,0,0,1", "LECHE FRESCA ENTERA CONAPROLE - SC 1 LT", 15.5, "http://www.devoto.com.uy/mvdcommerce/imgUpload/240501_gr.jpg",  ['Frescos', 'Frescos', 'Leches'])

    def test_minified_without_www_and_https(self):
        self.assertMinification("https://devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,528,0,0,1,1,3,3&basura=11#1202", "http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,528,0,0,1")

    def test_minified_with_www(self):
        self.assertMinification("http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,528,0,0,1,1,3,3&basura=11#1202", "http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,528,0,0,1")

if __name__ == '__main__':
    unittest.main()

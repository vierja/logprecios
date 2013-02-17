import unittest
from test_parser import TestParser


class TestDevotoParser(TestParser):

    def test_leche(self):
        self.assertValue("http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,528,0,0,1", 15.5)

    def test_leche_data(self):
        self.assertData("http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,528,0,0,1", "LECHE FRESCA ENTERA CONAPROLE - SC 1 LT", "http://www.devoto.com.uy/mvdcommerce/imgUpload/240501_gr.jpg",  ['Frescos', 'Frescos', 'Leches'])

    def test_hostname_with_www(self):
        self.assertHostname("http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,528,0,0,1", "devoto.com.uy")

    def test_hostname_without_www(self):
        self.assertHostname("http://devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,528,0,0,1", "devoto.com.uy")

    def test_hostname_with_https(self):
        self.assertHostname("https://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,528,0,0,1", "devoto.com.uy")

    def test_minified_without_www_and_https(self):
        self.assertMinification("https://devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,528,0,0,1,1,3,3&basura=11#1202", "http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,528,0,0,1")

    def test_minified_with_www(self):
        self.assertMinification("http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,528,0,0,1,1,3,3&basura=11#1202", "http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,528,0,0,1")

if __name__ == '__main__':
    unittest.main()

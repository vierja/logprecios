import unittest
import sys

sys.path.append('../../../../')
from parser.devoto import DevotoParser

class TestDevotoParser(unittest.TestCase):

    def assertValue(self, url, value):
        p = DevotoParser()
        site_value = p.get_value(url)
        assert site_value == value


    def test_leche(self):
        self.assertValue("http://www.devoto.com.uy/mvdcommerce/servlet/hdetalleproductop?2,1,528,0,0,1", 15.5)

if __name__ == '__main__':
    unittest.main()
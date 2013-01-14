import unittest
import sys

sys.path.append('../../../../')
from parser.multiahorro import MultiAhorroParser

class TestMultiAhorroParser(unittest.TestCase):

    def assertValue(self, url, value):
        p = MultiAhorroParser()
        site_value = p.get_value(url)
        assert site_value == value


    def test_leche_desc(self):
        self.assertValue("http://www.multiahorro.com.uy/Product.aspx?p=94295", 16)

if __name__ == '__main__':
    unittest.main()
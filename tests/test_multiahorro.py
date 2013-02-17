import unittest
from test_parser import TestParser


class TestMultiAhorroParser(TestParser):

    def test_leche_value(self):
        self.assertValue("http://www.multiahorro.com.uy/Product.aspx?p=94295", 16)

    def test_leche_data(self):
        self.assertData("http://www.multiahorro.com.uy/Product.aspx?p=94295", "LECHE CONAP. FRESCA DESCR. 1L", "http://www.multiahorro.com.uy/images/Products/small/610912.jpg", ['Productos Frescos', 'Lacteos', 'Leche', 'Leche Varios'])

    def test_cebolla_value(self):
        self.assertValue("http://www.multiahorro.com.uy/Product.aspx?p=106671", 29)

    def test_cebolla_data(self):
        self.assertData("http://www.multiahorro.com.uy/Product.aspx?p=106671", "CEBOLLA 1 Kg", "http://www.multiahorro.com.uy/images/Products/small/953150.jpg", ['Productos Frescos', 'Vegetales', 'Vegetales Varios'])

    def test_maxi_mix_value(self):
        self.assertValue("http://www.multiahorro.com.uy/Product.aspx?p=143292", 53)

    def test_maxi_mix_data(self):
        self.assertData("http://www.multiahorro.com.uy/Product.aspx?p=143292", "MAXI MIX WOLF 125G. 1 Kg", "http://www.multiahorro.com.uy/images/Products/small/634180.jpg", ["Alimentos Y Bebidas", "Alimentos", "Snaks", "Snaks Varios"])

if __name__ == '__main__':
    unittest.main()

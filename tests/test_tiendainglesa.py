# -*- coding: utf8 -*-
import unittest
from test_parser import TestParser


class TestTiendaInglesaParser(TestParser):

    def test_leche(self):
        self.assertValue("http://www.tinglesa.com.uy/producto.php?idarticulo=1531", 15.5)

    def test_leche_data(self):
        self.assertData("http://www.tinglesa.com.uy/producto.php?idarticulo=1531", "LECHE  CONAPROLE FRESCA ENTERA SACHET 1LT", "http://fotosti.e-tradeconsult.com/1200x900/VM000100/VM000161-1.jpg", ['Comestibles', u'Lácteos', 'Leches'])

    def test_tarjeta_sd_data(self):
        self.assertData("http://www.tinglesa.com.uy/producto.php?idarticulo=14610", "MEMORIA A-DATA MICRO SD / SD 4GB", "http://fotosti.e-tradeconsult.com/1200x900/VM221800/VM221871-1.jpg", [u"Electrónica", u"Computación", u"Cámaras - Filmadoras", u"Insumos"])

    def test_hostname_with_www(self):
        self.assertHostname("http://www.tinglesa.com.uy/producto.php?idarticulo=14610", "tinglesa.com.uy")

    def test_hostname_without_www(self):
        self.assertHostname("http://tinglesa.com.uy/producto.php?idarticulo=14610", "tinglesa.com.uy")

    def test_hostname_with_https(self):
        self.assertHostname("https://www.tinglesa.com.uy/producto.php?idarticulo=14610", "tinglesa.com.uy")

    def test_minified_without_www(self):
        self.assertMinification("https://tinglesa.com.uy/producto.php?idarticulo=14610&trash=10#tagged", "http://www.tinglesa.com.uy/producto.php?idarticulo=14610")

    def test_minified_with_www(self):
        self.assertMinification("http://www.tinglesa.com.uy/producto.php?idarticulo=14610&trash=10#tagged", "http://www.tinglesa.com.uy/producto.php?idarticulo=14610")

if __name__ == '__main__':
    unittest.main()

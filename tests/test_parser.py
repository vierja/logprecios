# -*- coding: utf8 -*-
import unittest
from tracker.tracker import get_parser


class TestParser(unittest.TestCase):

    def assertData(self, url, name, price, image_url, categories):
        parser = get_parser(url)
        res = parser.get_data()
        assert res['name'] == name
        assert res['price'] == price
        assert res['image_url'] == image_url
        assert all([x in res['categories'] for x in categories])
        assert all([x in categories for x in res['categories']])

    def assertMinification(self, url, minified):
        parser = get_parser(url)
        minified_res = parser.minify_url()
        assert minified_res == minified

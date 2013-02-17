# -*- coding: utf8 -*-
import unittest
from tracker.tracker import get_parser


class TestParser(unittest.TestCase):

    def assertValue(self, url, value):
        parser = get_parser(url)
        site_value = parser.get_price()
        assert site_value == value

    def assertData(self, url, name, image_url, categories):
        parser = get_parser(url)
        res = parser.get_data()
        assert res['name'] == name
        assert res['image_url'] == image_url
        assert all([x in res['categories'] for x in categories])
        assert all([x in categories for x in res['categories']])

    def assertHostname(self, url, hostname):
        parser = get_parser(url)
        hostname_res = parser.url_is_valid()
        assert hostname_res == hostname

    def assertMinification(self, url, minified):
        parser = get_parser(url)
        minified_res = parser.minify()
        assert minified_res == minified

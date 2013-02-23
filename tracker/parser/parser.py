import requests
from urlparse import urlparse


class Parser(object):
    def __init__(self, url):
        super(Parser, self).__init__()
        self.url = url
        self.opener = lambda url: requests.get(url, timeout=30, allow_redirects=False).text

    def get_hostname(self):
        o = urlparse(self.url)
        hostname = o.hostname
        if hostname.startswith('www.'):
            hostname = hostname[4:]
        return hostname

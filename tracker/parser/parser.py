import requests

class Parser(object):
    def __init__(self, url):
        super(Parser, self).__init__()
        self.url = url
        self.opener = lambda url: requests.get(url, timeout=30).text

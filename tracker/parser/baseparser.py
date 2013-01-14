from decimal import Decimal

class BaseParser(object):
    """Parser base para una interfaz en comun
    entre los distintos parsers."""
    def __init__(self):
        super(BaseParser, self).__init__()

    def get_value(url):
        pass

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def to_decimal(self, s):
        return Decimal(s)
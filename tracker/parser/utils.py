from decimal import Decimal

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def to_decimal(s):
    return Decimal(s)
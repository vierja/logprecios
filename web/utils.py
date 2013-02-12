import re
import unicodedata
import json
import datetime
import time

class DateTimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(time.mktime(obj.timetuple())*1e3 + obj.microsecond/1e3)
        else:
            return super(DateTimeJSONEncoder, self).default(obj)

def slugify(value):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.
    -- Shamefully stolen from Django
    """
    value = unicodedata.normalize('NFKD', unicode(value))
    value = value.encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)
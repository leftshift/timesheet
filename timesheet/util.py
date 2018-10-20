from datetime import datetime
from dateparser import parse

def try_parse(date):
    if date and not isinstance(date, datetime):
        date = parse(date, languages=['de'])

    return date

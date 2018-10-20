from datetime import datetime
from dateparser import parse
import calendar

def try_parse(date):
    if date and not isinstance(date, datetime):
        date = parse(date, languages=['de'])

    return date

def month_boundries(around):
    d1, d2 = calendar.monthrange(around.year, around.month)
    # cuz of course, the first day is the 0. (not)
    start = around.replace(day=d1+1)
    end = around.replace(day=d2)
    return start, end

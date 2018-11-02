from datetime import datetime
from dateparser import parse
import calendar
import click

def try_parse(date):
    if date and not isinstance(date, datetime):
        date = parse(date, languages=['de'])

    return date

def month_boundries(around):
    d1, d2 = calendar.monthrange(around.year, around.month)
    start = around.replace(day=1)
    end = around.replace(day=d2)
    return start, end

def iterate_events(res):
    for event in res:
        yield {
                "date": event.start.date(),
                "dur": event.duration,
                "note": event.note if event.note else ""
            }

def table(fstring, header, iterable):
    lines = []
    h = fstring.format(**header)
    h = click.style(h, bold=True)
    lines.append(h)

    for item in iterable:
        l = fstring.format(**item)
        lines.append(l)

    return "\n".join(lines)

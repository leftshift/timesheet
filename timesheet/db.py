from timesheet.models import Base, Event
from timesheet.util import month_boundries

import datetime
import statistics
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Db:
    def __init__(self, path):
        self.path = path
        self.engine = create_engine(path)
        self.Session = sessionmaker(bind=self.engine)

    def with_session(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            session = self.Session()
            return f(self, session, *args, **kwargs)
        return wrapper

    def require_clean(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            session = self.Session()
            open_events = session.query(Event).filter(Event.end==None).all()
            if len(open_events) == 1:
                raise ValueError("There is still an open session left")
            elif len(open_events) > 1:
                raise AssertionError("Database inconsistent, there is more than one open session")
            return f(self, *args, **kwargs)

        return wrapper

    def init_db(self):
        Base.metadata.create_all(self.engine)

    @with_session
    def _add_to_db(self, session, start, end, break_time):
        e = Event(start=start, end=end, break_mins=break_time)
        session.add(e)
        session.commit()

    @require_clean
    def add(self, start, end, break_time):
        delta = end - start
        if delta.total_seconds() / 60 < break_time:
            raise ValueError('break time is greater than total work time')
        self._add_to_db(start, end, break_time)

    @require_clean
    def add_start(self, start):
        if not start:
            start = datetime.datetime.now()
            start.replace(second=0, microsecond=0)
        self._add_to_db(start, None, None)

    @with_session
    def add_end(self, session, end, break_time):
        event = session.query(Event).filter(Event.end == None).one()
        event.end = end
        event.break_time = break_time

        session.add(event)
        session.commit()
        return event



    @with_session
    def get_range(self, session, start, end):
        r = TimeRange(session, start, end)
        return r

    @with_session
    def get_month(self, session, around):
        if not around:
            ## Do this to drop all time information
            around = datetime.datetime.now().date()
        start, end = month_boundries(around)
        return self.get_range(start, end)


class TimeRange():
    def __init__(self, session, start, end):
        if end < start:
            raise ValueError("End needs to be after start")
        self.session = session
        self.start = start
        self.end = end

    @property
    def duration(self):
        return self.end - self.start

    @property
    def events(self):
        res = self.session.query(Event)\
                .filter(Event.start >= self.start)\
                .filter((Event.end <= self.end) | (Event.end==None))
        return res.all()

    @property
    def total(self):
        return sum(self.events)

    @property
    def mean(self):
        if len(self.events) == 0:
            return datetime.timedelta(0)
        mean_sec = statistics.mean(float(e) for e in self.events)
        return datetime.timedelta(seconds=mean_sec)


class Week(TimeRange):
    def __init__(self, start, end):
        if end - start > datetime.timedelta(days=7):
            raise ValueError("Week can't be longer than 7 days")
        if (start.weekday() != 0) and (end.weekday() != 6):
            raise ValueError("Week has to start on Monday or end on Sunday")

        self.start = start
        self.end = end


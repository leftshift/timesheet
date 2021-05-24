from timesheet.models import Base, Event
from timesheet.util import month_boundries, week_boundries

import datetime
import statistics
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Db:
    """Access to a database, based on sqlalchemy."""

    def __init__(self, path):
        """
        :param path: SQLAlchemy database path to connect to.
            Examples: https://docs.sqlalchemy.org/en/latest/core/engines.html"""
        self.path = path
        self.engine = create_engine(path)
        self.Session = sessionmaker(bind=self.engine)

    def with_session(f):
        """Wraps function `f`, gives a sqlalchemy `session` as second argument"""
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            session = self.Session()
            return f(self, session, *args, **kwargs)
        return wrapper

    def require_clean(f):
        """Wraps function `f`, checks whether the database is 'clean',
        raises an Exception if it isn't.

        'clean' means there are no started sessions in the database,
        e.g. there are no events in the database with a start but
        without an end."""
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
        """Creates all required tables in the database."""
        Base.metadata.create_all(self.engine)

    @with_session
    def _add_to_db(self, session, start, end, break_time):
        e = Event(start=start, end=end, break_mins=break_time)
        session.add(e)
        session.commit()

    @require_clean
    def add(self, start, end, break_time):
        """Adds an event to the database.
        :param start, end: datetime.datetime objects for the begining and end
            of the work event.
        :param break_time: Break in the work event in minutes."""
        delta = end - start
        if delta.total_seconds() / 60 < break_time:
            raise ValueError('break time is greater than total work time')
        self._add_to_db(start, end, break_time)

    @require_clean
    def add_start(self, start):
        """Start a work session in the database.
        Adds an event with a start but without an end.
        :param start: datetime.datetime object for the beginning of the session.
            If this is None, the current time is used."""
        if not start:
            start = datetime.datetime.now()
            start.replace(second=0, microsecond=0)
        self._add_to_db(start, None, None)

    @with_session
    def add_end(self, session, end, break_time):
        """Ends a previously started work session.
        :param end: datetime.datetime object for the end of the session.
            If this is None, the current time is used."""
        event = session.query(Event).filter(Event.end == None).one()
        if not end:
            end = datetime.datetime.now()
            end.replace(second=0, microsecond=0)
        event.end = end
        event.break_time = break_time

        session.add(event)
        session.commit()
        return event



    @with_session
    def get_range(self, session, start, end):
        """Gets a :class:`TimeRange` object over the specified range.
        :param start, end: datetime.datetime objects for
            beginning and end of range."""
        r = TimeRange(session, start, end)
        return r

    @with_session
    def get_month(self, session, around):
        """Gets the :class:`TimeRange` object ranging over the month of `around`."""
        if not around:
            ## Do this to drop all time information
            around = datetime.datetime.now().date()
        start, end = month_boundries(around)
        return self.get_range(start, end)

    @with_session
    def get_week(self, session, around):
        """Gets the :class:`TimeRange` object ranging over the month of `around`."""
        if not around:
            ## Do this to drop all time information
            around = datetime.datetime.now().date()
        start, end = week_boundries(around)
        return self.get_range(start, end)


class TimeRange():
    """Represents a time range of events from a database."""
    def __init__(self, session, start, end):
        if end < start:
            raise ValueError("End needs to be after start")
        self.session = session
        self.start = start
        self.end = end

    @property
    def duration(self):
        """Length of the range as `datetime.timedelta`"""
        return self.end - self.start

    @property
    def events(self):
        """List of events in this range."""
        res = self.session.query(Event)\
                .filter(Event.start >= self.start)\
                .filter((Event.end <= self.end) | (Event.end==None))
        return res.all()

    @property
    def total(self):
        """Sum of durations of the events in this range.
        Returns datetime.timedelta."""
        return sum(self.events, datetime.timedelta(0))

    @property
    def mean(self):
        """Arithmetic mean of the events in this range."""
        if len(self.events) == 0:
            return datetime.timedelta(0)
        mean_sec = statistics.mean(float(e) for e in self.events)
        return datetime.timedelta(seconds=mean_sec)



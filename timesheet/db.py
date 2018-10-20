from timesheet.models import Base, Event
from timesheet.util import month_boundries

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

    def init_db(self):
        Base.metadata.create_all(self.engine)

    @with_session
    def add(self, session, start, end, break_time):

        delta = end - start
        if delta.total_seconds() / 60 < break_time:
            raise ValueError('break time is greater than total work time')

        e = Event(start=start, end=end, break_mins=break_time)
        session.add(e)
        session.commit()

    @with_session
    def get_range(self, session, start, end):
        res = session.query(Event).filter(Event.start >= start)\
                                  .filter(Event.end <= end)
        return res.all()

    @with_session
    def get_month(self, session, around):
        start, end = month_boundries(around)
        print(start, end)
        return self.get_range(start, end)


import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()

class Event(Base):
    __tablename__ = 'event'
    
    id = Column(Integer, primary_key=True)

    start = Column(DateTime)
    end = Column(DateTime)
    break_mins = Column(Integer, default=0)

    note = Column(String)

    @property
    def duration(self):
        if self.end:
            return self.end - self.start\
                    - datetime.timedelta(minutes=self.break_mins)
        else:
            return datetime.timedelta(0)

    def __float__(self):
        return self.duration.total_seconds()

    def __add__(self, other):
        return self.duration + other

    def __radd__(self, other):
        if other == 0:
            return self.duration
        else:
            return self.__add__(other)


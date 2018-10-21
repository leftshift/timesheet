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
    break_mins = Column(Integer)

    note = Column(String)

    @hybrid_property
    def duration(self):
        return self.end - self.start - datetime.timedelta(minutes=self.break_mins)


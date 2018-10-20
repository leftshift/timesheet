from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String

Base = declarative_base()

class Event(Base):
    __tablename__ = 'event'
    
    id = Column(Integer, primary_key=True)

    start = Column(DateTime)
    end = Column(DateTime)
    break_mins = Column(Integer)

    note = Column(String)

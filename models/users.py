from sqlalchemy import Column, String, Date, Integer, Numeric

from .base import Base


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    name = Column(String)
    handle = Column(String)
    location = Column(String)
    website = Column(String)
    date_joined = Column(Date)
    bio = Column(String)
    tweets = Column(String)
    twitter_page_url = Column(String)
    # height = Column(Integer)
    # weight = Column(Numeric)

    def __init__(self, name, date_joined, handle, location, website, bio, tweets, page_url):
        self.name = name
        self.date_joined = date_joined
        self.handle = handle
        self.location = location
        self.website = website
        self.bio = bio
        self.tweets = tweets
        self.page_url = page_url
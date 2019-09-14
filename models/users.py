from sqlalchemy import Column, String, Date, Integer, Numeric

from .base import Base


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    handle = Column(String, nullable=True)
    location = Column(String, nullable=True)
    website = Column(String, nullable=True)
    date_joined = Column(Date, nullable=True)
    bio = Column(String, nullable=True)
    tweets = Column(String, nullable=True)
    twitter_page_url = Column(String, nullable=True)
    is_scraped = Column(Integer, nullable=True)
    # height = Column(Integer)
    # weight = Column(Numeric)

    def __init__(self, name, date_joined, handle, location, website, bio, tweets, page_url, is_scraped):
        self.name = name
        self.date_joined = date_joined
        self.handle = handle
        self.location = location
        self.website = website
        self.bio = bio
        self.tweets = tweets
        self.page_url = page_url
        self.is_scraped = is_scraped

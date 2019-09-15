from sqlalchemy import Column, String, Date, Integer, Numeric

from .base import Base


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    name = Column(String(300), nullable=True)
    handle = Column(String(300), nullable=True)
    location = Column(String(300), nullable=True)
    website = Column(String(300), nullable=True)
    date_joined = Column(Date, nullable=True)
    bio = Column(String(300), nullable=True)
    tweets = Column(String(300), nullable=True)
    twitter_page_url = Column(String(300), nullable=True)
    is_scraped = Column(Integer, nullable=True)
    # height = Column(Integer)
    # weight = Column(Numeric)

    def __init__(self, name, date_joined, handle, location, website, bio, tweets, twitter_page_url, is_scraped):
        self.name = name
        self.date_joined = date_joined
        self.handle = handle
        self.location = location
        self.website = website
        self.bio = bio
        self.tweets = tweets
        self.twitter_page_url = twitter_page_url
        self.is_scraped = is_scraped

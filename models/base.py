import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

mysql_url = "mysql://{}:{}@localhost/{}".format(
    os.environ.get("DB_USERNAME", "root"),
    os.environ.get("DB_PASSWORD", "root"),
    os.environ.get("DB_NAME", "scrape_db")
)
engine = create_engine(mysql_url)
# use session_factory() to get a new Session
_SessionFactory = sessionmaker(bind=engine)

Base = declarative_base()


def session_factory():
    Base.metadata.create_all(engine)
    return _SessionFactory()
git
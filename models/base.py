import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

<<<<<<< HEAD
engine = create_engine('mysql://root:olorunfemi007@localhost:3306/twitter_table')
=======
mysql_url = "mysql+pymysql://{}:{}@localhost:8889/{}".format(
    os.environ.get("DB_USERNAME"),
    os.environ.get("DB_PASSWORD"),
    os.environ.get("DB_NAME", "scrape_db")
)
engine = create_engine(mysql_url)
>>>>>>> bd4732f8764b2d798d0a18484857aa4d31173de8
# use session_factory() to get a new Session
_SessionFactory = sessionmaker(bind=engine)

Base = declarative_base()


def session_factory():
    Base.metadata.create_all(engine)
    return _SessionFactory()
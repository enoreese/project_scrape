from datetime import date

from models.users import Person
from models.base import session_factory

from .scraper import ScrapeBot


class ScrapeUsers:

    def __init__(self):
        self.session = session_factory()

    def __get_users(self):
        users = self.session.query(Person).filter_by(is_scraped=0)
        self.session.close()
        return users.all()

    def run(self):
        users = self.__get_users()
        for user in users:
            ScrapeBot(url=user.twitter_page_url).run()

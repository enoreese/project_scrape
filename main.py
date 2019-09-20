from datetime import date
import multiprocessing as mp
import threading as th
from models.users import Person
from models.base import session_factory
import time
from scraper import UpdateBot
from scrapeusers import ScrapeBot
from scrapelog import ScrapeLog

print("loading logger")
logger = ScrapeLog()


class ScrapeUsers:

    def __init__(self):
        logger.info("Starting Scrape Bot...")
        logger.info("Starting SQL Factory...")
        self.session = session_factory()

    def __get_users(self):
        users = self.session.query(Person).filter_by(is_scraped=0)
        self.session.close()
        return users.all()

    def scrape(self):
        with open('hashtags.txt', 'r') as file:
            data = file.read().replace('\n', '')
            hashtags = data.split(",")
            for hashtag in hashtags:
                ScrapeBot(hashtag=hashtag).run()

    def update(self):
        while True:
            users = self.__get_users()
            if users:
                for user in users:
                    logger.info("Updating user: {}".format(user.handle))
                    UpdateBot(handle=str(user.handle)).run()
                    time.sleep(5)
            time.sleep(50)

    def run(self):
        logger.info("Starting Handles Scraper in Parallel")
        # self.scrape()
        # th.Thread(target=self.scrape()).start()
        scrape_handles = mp.Process(target=self.scrape)
        scrape_handles.start()

        logger.info("Starting Update Scraper in Parallel")
        # self.update()
        # th.Thread(target=self.update()).start()
        update_users = mp.Process(target=self.update)
        update_users.start()
        #
        # scrape_handles.join()
        #
        # update_users.join()


if __name__ == '__main__':
    ScrapeUsers().run()

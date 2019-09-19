import os
import time
import traceback
import sqlalchemy.exc
from selenium import webdriver, common
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

from models.users import Person
from models.base import session_factory
from scrapelog import ScrapeLog

logger = ScrapeLog()


class URL:
    # TWITTER = 'http://twitter.com/login'
    TWITTER = 'https://twitter.com/search?q=%23NigeriansLeaveSA&src=tyah'


class Constants:
    USERNAME = os.environ.get("TWITTER_USERNAME")
    PASSWORD = os.environ.get("TWITTER_PASSWORD")
    GLOBAL_ENTRY_Q = '#loan'


class TwitterLocator:
    username = (By.CLASS_NAME, "js-username-field")
    password = (By.CLASS_NAME, "js-password-field")
    submit_btn = (By.TAG_NAME, "button")
    search_input = (By.CLASS_NAME, "r-30o5oe")
    search_btn = (By.ID, "nav-search")
    tweets = (By.TAG_NAME, "article")
    like_btn = (By.XPATH,
                "//*[@id='react-root']/div/div/div/main/div/div/div/div[1]/div/div[2]/div/div/section/div/div/div/div[2]/div/article/div/div[2]/div[2]/div[4]/div[3]/div")
    latest_tweets = (By.PARTIAL_LINK_TEXT, 'Latest')
    handle = (By.CLASS_NAME, 'account-group')
    handle_real = (By.XPATH, '//span[@dir="ltr"]')
    bio = (By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div/div/div[1]/p')
    location = (By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/span[2]')
    website = (By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div/div/div[1]/div[2]/span[2]/a')
    date_joined = (By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div/div/div[1]/div[3]/span[2]')


class ScrapeBot(object):

    def __init__(self, hashtag, headless=True):
        self.locator_dictionary = TwitterLocator.__dict__
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(chrome_options=options, executable_path='driver/chromedriver')  # export PATH=$PATH:/path/to/chromedriver/folder
        url = "https://twitter.com/search?q=%23{}&src=tyah".format(hashtag)
        logger.info("Scraping hashtag: {}".format(hashtag))
        self.browser.get(url=url)

        self.timeout = 20
        self.scroll_pause_time = 7
        self.session = session_factory()
        self.handle = ""

    def view_latest_tweets(self):
        self.latest_tweets.click()

    def scroll(self):
        logger.info("Scrolling... ")
        # Get scroll height
        last_height = self.browser.execute_script("return document.body.scrollHeight")
        handles = self.browser.find_elements(*self.locator_dictionary['handle'])
        logger.info("Initial handles: {}".format(len(handles)))

        while True:
            print("Scrolling Down...")
            # Scroll down to bottom
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(self.scroll_pause_time)

            # Calculate new scroll height and compare with last scroll height
            try:
                new_height = self.browser.execute_script("return document.body.scrollHeight")
            except common.exceptions.TimeoutException as e:
                logger.warn(e)
                break

            print("New Height: ", new_height)

            handles = self.browser.find_elements(*self.locator_dictionary['handle'])
            logger.info("Gathered handles: {}".format(len(handles)))
            if new_height == last_height:
                break
            last_height = new_height
            print("Last Height: ", last_height)
            time.sleep(1)

    def add_user(self, handle, userid):
        user = Person(
            name='',
            date_joined='',
            handle=handle,
            location='',
            website='',
            bio='',
            tweets='',
            twitter_page_url='',
            is_scraped=0,
            user_id=userid
        )

        self.session.add(user)
        self.session.commit()

    def scrape_user(self):
        logger.info("Scrape users on page...")
        handles = self.browser.find_elements(*self.locator_dictionary['handle'])
        logger.info("len of handles: {}".format(len(handles)))
        for elements in handles:
            print(elements.text)
            handle = elements.text
            if handle and '@' in handle:
                handle = handle.split('@')[1]
                # handle_check = elements.find_element(*self.locator_dictionary['handle_real']).text
                print(handle)
                try:
                    user = self.session.query(Person).filter_by(handle=handle).first()
                except sqlalchemy.exc.InternalError as e:
                    logger.warn(e)

                if not user:
                    print('Not found duplicate...Skipping')
                    # handle_id = elements.find_element(*self.locator_dictionary['handle_real']).text
                    userids = elements.get_attribute("data-user-id")
                    print(userids)
                    self.add_user(handle=handle, userid=userids)

    def _find_element(self, *loc):
        return self.browser.find_element(*loc)

    def __getattr__(self, what):
        try:
            if what in self.locator_dictionary.keys():
                try:
                    element = WebDriverWait(self.browser, self.timeout).until(
                        EC.presence_of_element_located(self.locator_dictionary[what])
                    )
                except(TimeoutException, StaleElementReferenceException):
                    traceback.print_exc()

                try:
                    element = WebDriverWait(self.browser, self.timeout).until(
                        EC.visibility_of_element_located(self.locator_dictionary[what])
                    )
                except(TimeoutException, StaleElementReferenceException):
                    traceback.print_exc()

                try:
                    element = WebDriverWait(self.browser, self.timeout).until(
                        EC.element_to_be_clickable(self.locator_dictionary[what])
                    )
                except(TimeoutException, StaleElementReferenceException):
                    traceback.print_exc()
                # I could have returned element, however because of lazy loading, I am seeking the element before return
                return self._find_element(*self.locator_dictionary[what])
        except AttributeError:
            super(ScrapeBot, self).__getattribute__("method_missing")(what)

    def method_missing(self, what):
        print("No %s here!" % what)

    def run(self):
        print("running")
        self.scroll()
        self.scrape_user()
        self.browser.quit()

import os
import random
import time
import traceback
import boto3
import sqlalchemy.exc
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
# from pymemcache.client import base
from models.users import Person
from models.base import session_factory
from scrapelog import ScrapeLog


logger = ScrapeLog()

class URL:
    TWITTER = 'http://twitter.com/login'


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
    tweets = (By.CLASS_NAME, "js-stream-item")
    tweets_no = (By.XPATH, "/html/body/div[2]/div[2]/div/div[1]/div/div[2]/div/div/div[2]/div/div/ul/li[1]/a/span[3]")
    like_btn = (By.XPATH, "//*[@id='react-root']/div/div/div/main/div/div/div/div[1]/div/div[2]/div/div/section/div/div/div/div[2]/div/article/div/div[2]/div[2]/div[4]/div[3]/div")
    latest_tweets = (By.PARTIAL_LINK_TEXT, 'Latest')
    name = (By.CSS_SELECTOR, '.ProfileHeaderCard-nameLink')
    handle = (By.CSS_SELECTOR, '.ProfileHeaderCard-screennameLink > span:nth-child(1) > b:nth-child(1)')
    bio = (By.CSS_SELECTOR, '.ProfileHeaderCard-bio')
    location = (By.CSS_SELECTOR, '.ProfileHeaderCard-locationText')
    website = (By.CSS_SELECTOR, '.ProfileHeaderCard-periscopeProfileTextLink')
    date_joined = (By.CSS_SELECTOR, '.ProfileHeaderCard-joinDateText')


class UpdateBot(object):

    def __init__(self, handle, headless=True):
        self.locator_dictionary = TwitterLocator.__dict__
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(chrome_options=options, executable_path='driver/chromedriver')  # export PATH=$PATH:/path/to/chromedriver/folder
        logger.info("Updating DB for handle: {}".format(handle))
        url = "https://twitter.com/{}".format(str(handle).lower())
        print("URL: ", url)
        self.browser.get(url)
    
        self.timeout = 10
        self.scroll_pause_time = 5
        self.session = session_factory()
        self.handle = handle
        self.filename = ''

        # self.memc = base.Client(('localhost', 11211))

    def login(self, username=Constants.USERNAME, password=Constants.PASSWORD):
        # print(self.submit_btn)
        self.username.send_keys(username)
        self.password.send_keys(password)
        self.submit_btn.click()

    def search(self, q=Constants.GLOBAL_ENTRY_Q):
        self.search_input.send_keys(q)
        self.search_input.send_keys(Keys.ENTER)

    def view_latest_tweets(self):
        self.latest_tweets.click()

    def scroll_down(self, limit=100):
        tweets = self.browser.find_elements(*self.locator_dictionary['tweets'])
        tweets_no = self.browser.find_element(*self.locator_dictionary['tweets_no']).text
        if 'K' in tweets_no or 'M' in tweets_no:
            tweets_no = limit
        else:
            tweets_no = float(tweets_no.replace(',', ''))
        print("Tweets No: ", tweets_no)
        if tweets_no < limit:
            limit = tweets_no
        no_tweets = len(tweets)
        logger.info("initial No: {}".format(no_tweets))
        print("Limit: ", limit)
        while no_tweets < limit:
            # Scroll down to bottom
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")

            # Wait to load page
            time.sleep(self.scroll_pause_time)

            tweets = self.browser.find_elements(*self.locator_dictionary['tweets'])
            new_tweets = len(tweets)
            logger.info("Gathered {} tweets".format(new_tweets))

            if no_tweets == new_tweets:
                break
            no_tweets = new_tweets

    def like_tweet(self):
        """
        Like a random tweet
        :return:
        """
        tweets = self.browser.find_elements(*self.locator_dictionary['tweets'])
        tweet = random.choice(tweets)
        for twet in tweets:
            lik = twet.find_element(*self.locator_dictionary['like_btn'])
            lik.click()
            print("Liked Tweet: {}".format(twet.text))
            time.sleep(5)
        # like = tweet.find_element(*self.locator_dictionary['like_btn'])
        # like.click()
        # print("Liked Tweet: {}".format(tweet.text))
        # time.sleep(5)

    def add_tweet(self, tweets):
        logger.info("Adding tweets to S3...")
        s3 = boto3.resource('s3')
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        self.filename = "{}_tweets_{}.txt".format(self.handle, current_time)
        tweet_file = s3.Object(os.environ.get('BUCKET_NAME'), self.filename)
        tweet_file.put(Body=tweets)

    def update_user(self):
        logger.info("Updating User...")
        print("Handle: ", self.handle)

        user = self.session.query(Person).filter_by(handle=self.handle).first()
        try:
            name = self.browser.find_element(*self.locator_dictionary['name']).text
            name = name.encode('ascii', 'ignore').decode('ascii')
            print("Name: ", name)
        except sqlalchemy.exc.InternalError as e:
            logger.warn(e)
            name = ''
        user.name = name
        user.bio = self.browser.find_element(*self.locator_dictionary['bio']).text
        print("Bio: ", self.browser.find_element(*self.locator_dictionary['bio']).text)
        user.location = self.browser.find_element(*self.locator_dictionary['location']).text
        print("Location: ", self.browser.find_element(*self.locator_dictionary['location']).text)

        try:
            website = self.browser.find_element(*self.locator_dictionary['website']).text
            print("Website: ", self.browser.find_element(*self.locator_dictionary['website']).text)
        except NoSuchElementException as e:
            logger.warn(e)
            website = ''
        user.website = website
        user.date_joined = self.browser.find_element(*self.locator_dictionary['date_joined']).text
        print("Date Joined: ", self.browser.find_element(*self.locator_dictionary['date_joined']).text)

        self.session.add(user)
        self.session.commit()
        # self.session.close

    def mark_as_scraped(self):
        logger.info("Mark user as scraped")
        user = self.session.query(Person).filter_by(handle=self.handle).first()

        user.is_scraped = 1
        user.tweets = self.filename

        self.session.add(user)
        self.session.commit()
        # self.session.close

    def get_users(self):
        try:
            users = self.session.query(Person).filter_by(is_scraped=0)
        except sqlalchemy.exc.InternalError as e:
            logger.warn(e)

        return users

    def scrape_tweets(self):
        tweets = self.browser.find_elements(*self.locator_dictionary['tweets'])
        print("length of tweets: ", len(tweets))

        all_tweets = [tweet.text for tweet in tweets]
        all_tweets = ' '.join(all_tweets)

        self.add_tweet(tweets=all_tweets)

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
            super(UpdateBot, self).__getattribute__("method_missing")(what)

    def method_missing(self, what):
        logger.warn("No %s here!" % what)

    def run(self):
        self.update_user()
        self.scroll_down()
        time.sleep(2)
        self.scrape_tweets()
        self.mark_as_scraped()
        self.browser.quit()


class TestSelenium2():
    def __get_users(self):
        session = session_factory()
        users = session.query(Person).filter_by(is_scraped=0)
        session.close()
        users = users.all()
        users = [str(user.handle) for user in users]
        return users

    def test_update(self):
        while True:
            users = self.__get_users()
            for user in users:
                if user:
                    logger.info("Updating user: {}".format(user))
                    UpdateBot(handle=str(user)).run()
                    time.sleep(5)
            time.sleep(60)

#
# if __name__ == '__main__':
#     logger.info("Starting Update Scraper in Parallel")
#     # update_users = mp.Process(target=update)
#     # update_users.start()
#     #
#     # update_users.join()
#     update()
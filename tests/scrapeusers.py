import os
import time
import traceback
import json
import decimal
import boto3
from botocore.exceptions import ClientError
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from models.users import Person
from models.base import session_factory
from scrapelog import ScrapeLog

logger = ScrapeLog()


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


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
    down = (By.TAG_NAME, 'body')


class ScrapeBot(object):

    def __init__(self, hashtag, headless=True):
        self.locator_dictionary = TwitterLocator.__dict__
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(chrome_options=options,
                                        executable_path='../chromedriver')  # export PATH=$PATH:/path/to/chromedriver/folder
        url = "https://twitter.com/search?q=%23{}&src=tyah".format(hashtag)
        logger.info("Scraping hashtag: {}".format(hashtag))
        self.browser.get(url=url)

        self.no_of_pagedowns = 100

        self.timeout = 10
        self.scroll_pause_time = 3
        self.session = session_factory()
        self.handle = ""

    def view_latest_tweets(self):
        self.latest_tweets.click()

    def scroll(self):
        logger.info("Scrolling... ")
        # Get scroll height
        last_height = self.browser.execute_script(
            "return document.querySelectorAll('.stream-items > li.stream-item').length")
        handles = self.browser.find_elements(*self.locator_dictionary['handle'])
        logger.info("Initial handles: {}".format(len(handles)))
        last_handles = len(handles)

        i = 0
        while True:
            print("Scrolling down..., I: ", i)

            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(self.scroll_pause_time)

            elemsCount = self.browser.execute_script(
                "return document.querySelectorAll('.stream-items > li.stream-item').length")

            print("Elems count: ", elemsCount)

            try:
                WebDriverWait(self.browser, 20).until(
                    lambda x: x.find_element_by_xpath(
                        "//*[contains(@class,'stream-items')]/li[contains(@class,'stream-item')][" + str(
                            elemsCount + 1) + "]"))
            except:
                break

            if elemsCount == last_height:
                break
            last_height = elemsCount

            i += 1
        logger.info("Gathered handles: {}".format(len(self.browser.find_elements(*self.locator_dictionary['handle']))))

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

    def add_user_dynamo(self, handle, user_id):
        dynamodb = boto3.resource("dynamodb", region_name='us-west-2', endpoint_url="http://localhost:8000")

        table = dynamodb.Table('Person')

        response = table.put_item(
            Item={
                'handle': handle,
                'userid': user_id,
                'name': '',
                'location': '',
                'website': '',
                'bio': '',
                'tweets': '',
                'twitter_page_url': '',
                'is_scraped': 0,
            }
        )

        print("User Added to Dynamo DB:")
        print(json.dumps(response, indent=4, cls=DecimalEncoder))

    def scrape_user(self):
        logger.info("Scrape users on page...")
        handles = self.browser.find_elements(*self.locator_dictionary['handle'])
        logger.info("len of handles: {}".format(len(handles)))

        for handle in handles:
            if handle.text and '@' in handle.text:
                handle_txt = handle.text.split('@')[1]
                try:
                    userid = handle.get_attribute("data-user-id")
                except TimeoutException as e:
                    logger.warn(e)
                    userid = ''
                # print("User id: ", userid)
                # print("Handle: ", handle)
                self.add_user_dynamo(handle=handle_txt, user_id=userid)

        logger.info("Finish Scrape User tweet")

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


class TestSelenium1():
    def test_scrape(self):
        with open('hashtags.txt', 'r') as file:
            data = file.read().replace('\n', '')
            hashtags = data.split(",")
            for hashtag in hashtags:
                ScrapeBot(hashtag=hashtag).run()

# if __name__ == '__main__':
#     logger.info("Starting Handles Scraper in Parallel")
#     # scrape_handles = mp.Process(target=scrape)
#     # scrape_handles.start()
#     #
#     # scrape_handles.join()
#     scrape()

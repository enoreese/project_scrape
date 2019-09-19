import os
import random
import time
import traceback
import boto3
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from models.users import Person
from models.base import session_factory


class URL:
<<<<<<< HEAD
    TWITTER = 'http://twitter.com/login'
=======
    # TWITTER = 'http://twitter.com/login'
    TWITTER = 'https://twitter.com/search?q=%23NigeriansLeaveSA&src=tyah'
>>>>>>> bd4732f8764b2d798d0a18484857aa4d31173de8


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
<<<<<<< HEAD
    name = (By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div/div/div[1]/h1/a')
    handle = (By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div/div/div[1]/h2/a/span/b')
=======
    handle = (By.CLASS_NAME, 'account-group')
    handle_real = (By.CSS_SELECTOR, 'span.username')
>>>>>>> bd4732f8764b2d798d0a18484857aa4d31173de8
    bio = (By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div/div/div[1]/p')
    location = (By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/span[2]')
    website = (By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div/div/div[1]/div[2]/span[2]/a')
    date_joined = (By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div/div/div[1]/div[3]/span[2]')


class ScrapeBot(object):

    def __init__(self):
        self.locator_dictionary = TwitterLocator.__dict__
<<<<<<< HEAD
        print("Loadoing......")

=======
        print("Loading....")
>>>>>>> bd4732f8764b2d798d0a18484857aa4d31173de8
        self.browser = webdriver.Chrome('/usr/local/bin/chromedriver')  # export PATH=$PATH:/path/to/chromedriver/folder
        self.browser.get(URL.TWITTER)

        self.timeout = 10
        self.scroll_pause_time = 5
        self.session = session_factory()
        self.handle = ""

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

    def scroll_down(self, limit=50):
        tweets = self.browser.find_elements(*self.locator_dictionary['tweets'])
        no_tweets = len(tweets)
        while no_tweets < limit:
            # Scroll down to bottom
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")

            # Wait to load page
            time.sleep(self.scroll_pause_time)

            tweets = self.browser.find_elements(*self.locator_dictionary['tweets'])
            no_tweets = len(tweets)

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
        s3 = boto3.resource('s3')
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        filename = "{}_tweets_{}.txt".format(self.handle, current_time)
        tweet_file = s3.Object(os.environ.get('BUCKET_NAME'), filename)
        tweet_file.put(Body=tweets)

    def update_user(self):
        self.handle = self.browser.find_element(*self.locator_dictionary['handle']).text

        user = self.session.query(Person).filter_by(self.handle)
        user.name = self.browser.find_element(*self.locator_dictionary['name']).text
        user.handle = self.handle
        user.bio = self.browser.find_element(*self.locator_dictionary['bio']).text
        user.location = self.browser.find_element(*self.locator_dictionary['location']).text
        user.website = self.browser.find_element(*self.locator_dictionary['website']).text
        user.date_joined = self.browser.find_element(*self.locator_dictionary['date_joined']).text

        self.session.add(user)
        self.session.commit()
<<<<<<< HEAD
        self.session.close
=======
        # self.session.close

    def scroll(self):
        time.sleep(5)
        lenOfPage = self.browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        time.sleep(5)
        match = False
        while (match == False):
            lastCount = lenOfPage
            time.sleep(3)
            lenOfPage = self.browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")

            self.browser.find_element_by_tag_name('body').send_keys(Keys.END)
            print('scrolling...')
            time.sleep(5)
            if lastCount == lenOfPage:
                match = True
                print('end of scrolling...')
                time.sleep(10)


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
        handles = self.browser.find_elements(*self.locator_dictionary['handle'])
        print(handles)
        print("handelsssnijdiidjdj")
        for elements in handles:

            print(elements)
            handle_check = elements.find_element(*self.locator_dictionary['handle_real']).text
            user = self.session.query(Person).filter_by(handle=handle_check).first()
            if not user:
                print('Not found duplicate...Skipping')
                handle_id = elements.find_element(*self.locator_dictionary['handle_real']).text
                userids = elements.get_attribute("data-user-id")
                self.add_user(handle=handle_id, userid=userids)


            # handle_id = elements.text

                print(userids)
                print(handle_id)

            # self.mark_as_scraped()



>>>>>>> bd4732f8764b2d798d0a18484857aa4d31173de8

    def mark_as_scraped(self):
        user = self.session.query(Person).filter_by(self.handle)

        user.is_scraped = 1

        self.session.add(user)
        self.session.commit()
<<<<<<< HEAD
        self.session.close
=======
        # self.session.close
>>>>>>> bd4732f8764b2d798d0a18484857aa4d31173de8

    def scrape_tweets(self):
        all_tweets = ""
        tweets = self.browser.find_elements(*self.locator_dictionary['tweets'])
        for tweet in tweets:
            all_tweets = all_tweets + tweet.text

        self.add_tweet(tweets=all_tweets)
        self.mark_as_scraped()

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
        # self.login()
        # self.search()
        # self.view_latest_tweets()
<<<<<<< HEAD
        self.update_user()
        self.scroll_down()
        time.sleep(2)
        self.scrape_tweets()
        self.browser.quit()


if __name__ == '__main__':
    ScrapeBot().run()
=======
        # self.update_user()
        # self.scroll_down()
        # time.sleep(2)
        # self.scrape_tweets()
        self.scroll()
        self.scrape_user()
        # self.browser.quit()

if __name__ == '__main__':
    ScrapeBot().run()






>>>>>>> bd4732f8764b2d798d0a18484857aa4d31173de8

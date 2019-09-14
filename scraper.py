import os
import random
import time
import traceback

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


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
    tweets = (By.TAG_NAME, "article")
    like_btn = (By.XPATH, "//*[@id='react-root']/div/div/div/main/div/div/div/div[1]/div/div[2]/div/div/section/div/div/div/div[2]/div/article/div/div[2]/div[2]/div[4]/div[3]/div")
    latest_tweets = (By.PARTIAL_LINK_TEXT, 'Latest')
    user = (By.XPATH, '')
    handle = (By.XPATH, '')



class LikeBot(object):

    def __init__(self):
        self.locator_dictionary = TwitterLocator.__dict__
        self.browser = webdriver.Chrome('/usr/local/bin/chromedriver')  # export PATH=$PATH:/path/to/chromedriver/folder
        self.browser.get(URL.TWITTER)
        self.timeout = 10

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

    def gather_tweets(self):
        tweets = self.browser.find_elements(*self.locator_dictionary['tweets'])
        for tweet in tweets:
            enter_user(tweet)
            scrape_user()

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
            super(LikeBot, self).__getattribute__("method_missing")(what)

    def method_missing(self, what):
        print ("No %s here!" % what)

    def run(self):
        self.login()
        self.search()
        self.view_latest_tweets()
        time.sleep(2)
        self.like_tweet()
        self.browser.quit()

if __name__ == "__main__":
    LikeBot().run()
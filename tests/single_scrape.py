import os
import time
import traceback
import json
import decimal
import boto3
import twint

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


class ScrapeBot(object):

    def __init__(self, handle):
        self.handle = handle
        self.filename = None
        logger.info("Scraping for handle: {}".format(handle))
        self.user_config = twint.Config()
        self.tweet_config = twint.Config()

        self.user_config.Username = handle
        # self.user_config.Format = "ID {id} | Name {name} | Bio {bio} | Location {location} | Join Date {join_date}"
        self.user_config.Store_object = True
        self.user_config.User_full = True

        self.tweet_config.Username = handle
        self.tweet_config.Limit = 120
        self.tweet_config.Store_object = True

    def __lookup(self):
        twint.run.Lookup(self.user_config)
        return twint.output.users_list

    def __scrape_tweets(self):
        twint.run.Search(self.tweet_config)
        return twint.output.tweets_list

    def add_user_dynamo(self,
                        name,
                        date_joined,
                        handle,
                        location,
                        website,
                        bio,
                        tweets,
                        user_id
                        ):
        logger.info("Adding user to DynamoDB...")
        dynamodb = boto3.resource("dynamodb", region_name='us-east-2')

        table = dynamodb.Table('person')

        response = table.put_item(
            Item={
                'handle': handle,
                'userid': user_id,
                'is_scraped': 1,
                'twitter_name': name,
                'date_joined': date_joined,
                'twitter_location': location,
                'website': website,
                'bio': bio,
                'tweets': tweets
            }
        )

        print("User Added to Dynamo DB:")
        print(json.dumps(response, indent=4, cls=DecimalEncoder))

    def add_tweet(self, tweets):
        logger.info("Adding tweets to S3...")
        s3 = boto3.resource('s3')
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        self.filename = "{}_tweets_{}.txt".format(self.handle, current_time)
        tweet_file = s3.Object(os.environ.get('BUCKET_NAME'), self.filename)
        tweet_file.put(Body=tweets)

    def run(self):
        logger.info("User lookup")
        user = self.__lookup()
        user = user[0]
        logger.info("Tweets lookup")
        tweets = self.__scrape_tweets()

        tweets = [tweet.tweet for tweet in tweets]
        tweets = ' '.join(tweets)

        self.add_tweet(tweets)
        self.add_user_dynamo(
            handle=self.handle,
            user_id=user.id if user.id else 'empty',
            bio=user.bio if user.bio else 'empty',
            date_joined=user.join_date if user.join_date else 'empty',
            location=user.location if user.location else 'empty',
            name=user.name if user.name else 'empty',
            tweets=self.filename,
            website=user.url if user.url else 'empty'
        )


class TestSelenium1():
    def test_scrape(self):
        with open('demola_followers.txt', 'r') as file:
            data = file.readlines()
        content = [x.strip() for x in data]
        for handle in content:
            try:
                ScrapeBot(handle=handle).run()
            except Exception as e:
                logger.warn(e)
                time.sleep(3)
                ScrapeBot(handle=handle).run()


if __name__ == '__main__':
    logger.info("Starting Handles Scraper in Parallel")
    TestSelenium1().test_scrape()

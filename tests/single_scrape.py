import os
import time
import traceback
import json
import decimal
import boto3
import twint
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

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

    def __init__(self, handle=None, i=None):
        self.handle = handle
        self.filename = None
        self.i = i
        # logger.info("Scraping for handle: {}".format(self.handle))

    def __get_users(self):
        dynamodb = boto3.resource("dynamodb", region_name='us-east-2')
        users = []
        table = dynamodb.Table('person')
        try:
            response = table.scan(
                FilterExpression=Attr('is_scraped').eq(0)
            )
        except ClientError as e:
            logger.warn(e.response['Error']['Message'])
        else:
            users = response['Items']
            print("GetItem succeeded:")
            # users = json.dumps(item, indent=4, cls=DecimalEncoder)

        users = [user['handle'] for user in users]
        return users

    def __lookup(self, handle):
        user_config = twint.Config()
        user_config.Username = handle
        # self.user_config.Format = "ID {id} | Name {name} | Bio {bio} | Location {location} | Join Date {join_date}"
        user_config.Store_object = True
        user_config.User_full = True

        twint.run.Lookup(user_config)
        return twint.output.users_list

    def __scrape_tweets(self, handle):
        tweet_config = twint.Config()
        tweet_config.Username = handle
        tweet_config.Limit = 120
        tweet_config.Store_object = True
        twint.run.Search(tweet_config)
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
        # logger.info("Adding user to DynamoDB...")
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

    def mark_as_scraped_dynamo(self, handle):
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

        table = dynamodb.Table('person')

        response = table.update_item(
            Key={
                'handle': handle,
            },
            UpdateExpression="set is_scraped= :s, tweets=:t",
            ExpressionAttributeValues={
                ':s': 1,
                ':t': self.filename,
            },
            ReturnValues="UPDATED_NEW"
        )

        print("User updated:")
        print(json.dumps(response, indent=4, cls=DecimalEncoder))

    def run(self):
        logger.info("User lookup: {}".format(self.i))
        user = self.__lookup(self.handle)
        print(user)
        user = user[self.i]
        print(user.name)
        logger.info("Tweets lookup")
        tweets = self.__scrape_tweets(self.handle)

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

    def run2(self):
        users = self.__get_users()
        logger.info("Length of Users: {}".format(len(users)))
        for user in users:
            self.handle = user
            logger.info("User lookup: {}".format(user))
            logger.info("Tweets lookup")
            tweets = self.__scrape_tweets(user)

            tweets = [tweet.tweet for tweet in tweets]
            tweets = ' '.join(tweets)

            self.add_tweet(tweets)
            self.mark_as_scraped_dynamo(user)


class TestSelenium1:
    def test_scrape(self):
        with open('demola_followers.txt', 'r') as file:
            data = file.readlines()
        contents = [x.strip() for x in data]
        i=0
        for content in contents:
            try:
                ScrapeBot(handle=content, i=i).run()
                i += 1
            except (Exception, IndexError) as e:
                logger.warn(e)
                time.sleep(3)
                # ScrapeBot(handle=content[i], i=i).run()

    def scrape2(self):
        try:
            ScrapeBot().run2()
        except (Exception, IndexError) as e:
            logger.warn(e)
            time.sleep(3)


if __name__ == '__main__':
    logger.info("Starting Update Scraper in Parallel")
    TestSelenium1().scrape2()

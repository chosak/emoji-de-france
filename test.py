import os

from twython import Twython



consumer_key = os.environ['TWITTER_CONSUMER_KEY']
consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
access_key = os.environ['TWITTER_ACCESS_KEY']
access_secret = os.environ['TWITTER_ACCESS_SECRET']

twitter = Twython(
    consumer_key,
    consumer_secret,
    access_key,
    access_secret
)

print twitter.search(q='python')
twitter.update_status(status='test post')

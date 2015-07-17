import argparse
import os
import requests

from twython import Twython


MAX_TWEET_LENGTH = 140

hashtag = '#TDF2015'
smile = '\U0001f604'
car = '\U0001f697'
bike = '\U0001f6b4'
flag = '\U0001f3c1'


def get_status():
    pass


def compose_tweet(status):
    status = ' {}'.format(hashtag)
    status = bike * (MAX_TWEET_LENGTH - len(status)) + status
    return status


def twitter_api():
    return Twython(*(os.environ[k] for k in (
        'TWITTER_CONSUMER_KEY',
        'TWITTER_CONSUMER_SECRET',
        'TWITTER_ACCESS_KEY',
        'TWITTER_ACCESS_SECRET'
    )))


def tweet_tdf(debug=True):
    status = get_status()
    tweet = compose_tweet(status)
    print('{} characters'.format(len(tweet)))
    print(tweet)

    if not debug:
        twitter = twitter_api()
        twitter.update_status(status=tweet)


if '__main__' ==  __name__:
    parser = argparse.ArgumentParser(description='Tweet TdF status')
    parser.add_argument('--debug', action='store_true',
                        help='compose tweet, but don\'t send it out')
    args = parser.parse_args()

    tweet_tdf(debug=args.debug)

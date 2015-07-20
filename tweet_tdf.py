import argparse
import os
import requests

from twython import Twython


MAX_TWEET_LENGTH = 140

HASHTAG = '#TDF2015'

EMOJIS = {
    'smile': '\U0001f604',
    'car': '\U0001f697',
    'bike': '\U0001f6b4',
    'checkered_flag': '\U0001f3c1',
    'clock': '\U0001f551',
}


def get_status():
    state = requests.get(
        'http://www.letour.fr/useradgents/2015/json/appState.json'
    ).json()
    stage = state['stage']

    riders_version = state['jsonVersions']['starters']
    riders = requests.get(
        'http://www.letour.fr/useradgents/2015/json/starters.{}.json'.format(
            riders_version
        )
    ).json()

    riders = {
        r['n']: {
            'first': r['f'],
            'last': r['l'],
            'name': r['s'],
        } for r in riders['r']
    }

    live = requests.get(
        'http://www.letour.fr/useradgents/2015/json/livestage{}.json'.format(
            stage
        )
    ).json()

    km_covered = live['kp']
    km_remaining = live['kr']
    groups = [
        {
            'peloton': 'Peloton' == g['t'],
            'number': g.get('n'),
            'members': [r['r'] for r in g.get('r', [])],
        } for g in live['g']
    ]

    return {
        'stage': int(stage[:2]),
        'km_covered': km_covered,
        'km_remaining': km_remaining,
        'groups': groups,
        'riders': riders,
    }


def compose_tweet(status):
    def fmt(line, **kwargs):
        d = kwargs.copy()
        d.update(EMOJIS)
        return line.format(**d)

    lines = [fmt('{checkered_flag} {km_remaining} km to go', **status)]

    for group in status['groups']:
        if group['peloton']:
            group_line = fmt('{bike}' * 8)
        elif group['number'] > 1:
            group_line = fmt('{bike} {number}', **group)
        else:
            rider = status['riders'][group['members'][0]]['name']
            group_line = fmt('{bike} {rider}', rider=rider)
        lines.append(group_line)

    lines.append(HASHTAG)

    return '\n'.join(lines)
    #status = bike * (MAX_TWEET_LENGTH - len(status)) + status
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
    #print('{} characters'.format(len(tweet)))
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

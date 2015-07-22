import argparse
import os
import requests

from twython import Twython

from twitter_accounts import TWITTER_ACCOUNTS


MAX_TWEET_LENGTH = 140
SHOW_GROUPS = False

HASHTAG = '#TDF2015'

EMOJIS = {
    'smile': '\U0001f604',
    'car': '\U0001f697',
    'bike': '\U0001f6b4',
    'checkered_flag': '\U0001f3c1',
    'clock': '\U0001f551',
}

JERSEYS = {
    'y': '#MaillotJaune',
    'r': '#MaillotaPois',
    'g': '#MaillotVert',
    'w': '#MaillotBlanc',
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

    #for v in sorted(riders.values(), key=lambda k: k['last']):
    #    print(v['first'] + ' ' + v['last'] + ' ' + v['name'])

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
            'seconds_back': g.get('d', 0),
            'jerseys': g.get('j', []),
        } for g in live['g']
    ]

    return {
        'stage': int(stage[:2]),
        'km_covered': km_covered,
        'km_remaining': km_remaining,
        'groups': groups,
        'riders': riders,
    }


def format_seconds(s):
    if s < 60:
        return ':{}'.format(s)
    minutes = int(s / 60)
    return '{}:{:02d}'.format(minutes, s - (minutes * 60))


def compose_tweet(status):
    def fmt(line, **kwargs):
        d = kwargs.copy()
        d.update(EMOJIS)
        return line.format(**d)

    lines = [
        HASHTAG + ' Stage {}'.format(status['stage']),
        fmt('{checkered_flag} {km_remaining} km to go!', **status),
    ]

    seen_peloton = False
    for i, group in enumerate(status['groups']):
        group_line = '{bike}'

        is_peloton = group['peloton']
        if is_peloton:
            group_line += ' Peleton'
            seen_peloton = True
        else:
            num = group['number']
            if num > 1:
                group_line += ' x {}'.format(num)

        if not is_peloton and seen_peloton:
            break

        seconds_back = group['seconds_back']
        if seconds_back:
            group_line += ' {clock} ' + format_seconds(seconds_back)

        if not seen_peloton and not is_peloton:
            rider_keys = group['members']
            riders = [status['riders'][k] for k in rider_keys]

            if len(riders) <= 4:
                names = []
                for rider in riders:
                    names.append(get_rider_name(rider))
                group_line += ' {}'.format(' '.join(names))
        elif SHOW_GROUPS:
            group_line += ' ' + ' '.join(JERSEYS[j] for j in group['jerseys'])

        group_line = fmt(group_line)
        lines.append(group_line)

    return '\n'.join(lines)


def get_rider_name(rider):
    name = rider['name']
    return TWITTER_ACCOUNTS.get(
        rider['name'],
        '#' + rider['last'].replace(' ', '').lower().strip()
    )


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

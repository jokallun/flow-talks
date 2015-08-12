# -*- coding: utf-8 -*-
import os
import twitter
from websocket import create_connection
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limits = [20, 30, 40]
tweetlist = [u'On liian kylmä', u'Nyt on hyvä', u'Turhan lämmin', u'Ihan liian kuuma']
TWEEW_INTERVAL = 10.0

def get_twitter_client():
    CONSUMER_KEY = 'mDW8dNVXrioYiSjse9hneaDGy'
    CONSUMER_SECRET = 'jg0A2CcHaVSBWfsOqhgABUxQoZUx7sstEk9NSVUbVphkGJr1Zb'

    oauth_filename = 'credentials'
    if not os.path.exists(oauth_filename):
        twitter.oauth_dance("ruukku", CONSUMER_KEY, CONSUMER_SECRET, oauth_filename)

    oauth_token, oauth_secret = twitter.read_token_file(oauth_filename)

    auth = twitter.OAuth(oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET)
    return twitter.Twitter(auth=auth)


def get_socket_data(ws, location, msg, sensor_name):
    data = json.loads(ws.recv())
    logger.debug(data)
    if data.get('msg') != msg or data.get('name') != location:
        return {}
    sensor = [s for s in data.get('sensors') if s.get('name') == sensor_name]
    if len(sensor) == 0:
        return {}
    sd = sensor[0]
    sd['timestamp'] = data.get('timestamp')
    return sd

def get_tweet(value, current_state, last_tweet_time):
    state = 0
    for limit in limits:
        if value > limit:
            state += 1
    if state != current_state and (time.time() - last_tweet_time) > TWEEW_INTERVAL:
        return (tweetlist[state] + u'. Lämpötila: {}'.format(value), state)
    else:
        return (None, current_state)

def main():
    ws = create_connection("ws://88.198.19.60:9001/")
    tw_client = get_twitter_client()
    current_state = 0
    counter = 0
    last_tweet_time = 0

    while True:
        try:
            # data = get_socket_data(ws, 'Analog Sensor Data', 'Soil moisture')
            # data = get_socket_data(ws, 'Light Sensor Data', 'Illuminance')
            data = get_socket_data(ws, 'Parrulaituri', 'Barometer Sensor Data', 'Temperature')
            value = data.get(u'value')
            if value is None:
                continue
            tweet, current_state = get_tweet(value, current_state, last_tweet_time)
            logger.debug(tweet, current_state, value)
            if tweet is not None:
                tw_client.statuses.update(status=tweet)
                last_tweet_time = time.time()
        except Exception as e:
            logger.exception(e)
            ws = create_connection("ws://88.198.19.60:9001/")
            tw_client = get_twitter_client()
        counter += 1
        if counter > 300:
            break

if __name__ == '__main__':
    main()

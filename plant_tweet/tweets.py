# -*- coding: utf-8 -*-
import os
import twitter
from websocket import create_connection
import json

def get_twitter_client():
    CONSUMER_KEY = 'mDW8dNVXrioYiSjse9hneaDGy'
    CONSUMER_SECRET = 'jg0A2CcHaVSBWfsOqhgABUxQoZUx7sstEk9NSVUbVphkGJr1Zb'

    oauth_filename = 'credentials'
    if not os.path.exists(oauth_filename):
        twitter.oauth_dance("ruukku", CONSUMER_KEY, CONSUMER_SECRET, oauth_filename)

    oauth_token, oauth_secret = twitter.read_token_file(oauth_filename)

    auth = twitter.OAuth(oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET)
    return twitter.Twitter(auth=auth)


def get_socket_data(ws, msg, sensor_name):
    data = json.loads(ws.recv())
    if data.get('msg') != msg:
        return None
    sensor = [s for s in data.get('sensors') if s.get('name') == sensor_name]
    if len(sensor) == 0:
        return None
    sd = sensor[0]
    sd['timestamp'] = data.get('timestamp')
    return sd

ws = create_connection("ws://88.198.19.60:9001/")
tw_client = get_twitter_client()

limit_value = 700
counter = 0

while True:
    try:
        # data = get_socket_data(ws, 'Analog Sensor Data', 'Soil moisture')
        data = get_socket_data(ws, 'Light Sensor Data', 'Illuminance')
        if data.get('value') < limit_value:
            tw_client.statuses.update(status=u"Tulipas pimeää! Luxeja {}".format(data.get('value')))
            limit_value = limit_value - 100
    except:
        ws = create_connection("ws://88.198.19.60:9001/")
        tw_client = get_twitter_client()
    counter += 1
    if counter > 1000:
        break

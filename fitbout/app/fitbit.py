from datetime import datetime
from django.conf import settings
from oauthlib import oauth1
import requests


class Client(object):
    '''
    A client for interacting with Fitbit's API. Requires OAuth user token key/secret.
    '''
    def __init__(self, key, secret):
        self.client = oauth1.Client(settings.FITBIT_KEY, settings.FITBIT_SECRET, key, secret)

    def get(self, url):
        url = 'https://api.fitbit.com' + url
        url, headers, params = self.client.sign(url)
        r = requests.get(url, headers=headers, params=params)
        return r.json()

    def get_activities(self, date=None):
        if not date:
            date = datetime.now()

        return self.get('/1/user/-/activities/date/{0}-{1}-{2}.json'.format(date.year, date.month, date.day))

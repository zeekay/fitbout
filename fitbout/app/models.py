from mongoengine import Document, DynamicDocument, DateTimeField, FloatField, ListField, ReferenceField, StringField, URLField
from mongoengine.django import auth

from . import fitbit


class Activity(DynamicDocument):
    '''
    Record of activity returned by Fitbit API encompassing a single day of
    activity.
    '''
    user = ReferenceField('User')
    date = DateTimeField(unique_with='user')

    @property
    def steps(self):
        return self.summary['steps']

    @property
    def calories(self):
        return self.summary['caloriesOut']

    @property
    def active_score(self):
        return self.summary['activeScore']


class Competition(Document):
    name        = StringField()
    start       = DateTimeField()
    end         = DateTimeField()
    competitors = ListField(ReferenceField('User'))

    @property
    def _competitors(self):
        '''
        Hack to show everyone
        '''
        return User.objects.all()

    @property
    def stats(self):
        '''
        Return stats for each competitor.
        '''
        female_steps      = [(i, c) for i, c in enumerate(sorted((c for c in self._competitors if c.gender == 'female'), key=lambda c: c.steps, reverse=True), start=1)]
        male_steps        = [(i, c) for i, c in enumerate(sorted((c for c in self._competitors if c.gender == 'male'), key=lambda c: c.steps, reverse=True), start=1)]
        male_most_steps   = [(i, c) for i, c in enumerate(sorted((c for c in self._competitors if c.gender == 'male'), key=lambda c: c.most_steps, reverse=True), start=1)]
        female_most_steps = [(i, c) for i, c in enumerate(sorted((c for c in self._competitors if c.gender == 'female'), key=lambda c: c.most_steps, reverse=True), start=1)]

        return {'male_steps': male_steps,
                'female_steps': female_steps,
                'male_most_steps': male_most_steps,
                'female_most_steps': female_most_steps}


class User(auth.User):
    avatar      = URLField()
    height      = FloatField()
    weight      = FloatField()
    city        = StringField()
    state       = StringField()
    country     = StringField()
    nickname    = StringField()
    full_name   = StringField()
    gender      = StringField()
    birthdate   = DateTimeField()
    fitbit_id   = StringField()
    activities  = ListField(ReferenceField('Activity'))
    social_auth = ReferenceField('UserSocialAuth')

    @property
    def tokens(self):
        '''
        Return oauth tokens for Fitbit API.
        '''
        tokens = self.social_auth.tokens
        return tokens['oauth_token'], tokens['oauth_token_secret']

    @property
    def client(self):
        '''
        Client for interacting with Fitbit API.
        '''
        if hasattr(self, '_client'):
            return self._client
        self._client = fitbit.Client(*self.tokens)
        return self._client

    def get_activities(self, date=None):
        '''
        Get activities by date from Fitbit API.
        '''
        return self.client.get_activities(date)

    @property
    def steps(self):
        return sum(a.steps for a in self.activities)

    @property
    def most_steps(self):
        return max(a.steps for a in self.activities or [0])

    @property
    def calories(self):
        return sum(a.calories for a in self.activities)

    @property
    def active_score(self):
        return sum(a.active_score for a in self.activities)

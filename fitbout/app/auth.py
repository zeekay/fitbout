from social.apps.django_app.me.models import DjangoStorage
from social.backends.oauth import BaseOAuth1
from mongoengine import Document, DictField, ReferenceField, StringField, signals
from social.storage.django_orm import DjangoUserMixin
import six

from .models import User


class UserSocialAuth(Document, DjangoUserMixin):
    """
    Social Auth association model
    """
    user = ReferenceField('User')
    provider = StringField(max_length=32)
    uid = StringField(max_length=255, unique_with='provider')
    extra_data = DictField()

    def str_id(self):
        return str(self.id)

    @classmethod
    def get_social_auth_for_user(cls, user, provider=None, id=None):
        qs = cls.objects
        if provider:
            qs = qs.filter(provider=provider)
        if id:
            qs = qs.filter(id=id)
        return qs.filter(user=user)

    @classmethod
    def create_social_auth(cls, user, uid, provider):
        if not isinstance(type(uid), six.string_types):
            uid = str(uid)
        return cls.objects.create(user=user, uid=uid, provider=provider)

    @classmethod
    def username_max_length(cls):
        return UserSocialAuth.user_model().username.max_length

    @classmethod
    def user_model(cls):
        return User

    @classmethod
    def create_user(cls, *args, **kwargs):
        kwargs['password'] = '!'
        if 'email' in kwargs:
            kwargs['email'] = kwargs['email'] or None
        return cls.user_model().create_user(*args, **kwargs)

    @classmethod
    def allowed_to_disconnect(cls, user, backend_name, association_id=None):
        if association_id is not None:
            qs = cls.objects.filter(id__ne=association_id)
        else:
            qs = cls.objects.filter(provider__ne=backend_name)
        qs = qs.filter(user=user)

        if hasattr(user, 'has_usable_password'):
            valid_password = user.has_usable_password()
        else:
            valid_password = True

        return valid_password or qs.count() > 0

    @classmethod
    def post_save(cls, sender, document, created=False):
        '''
        Post save event (fired from UserSocialAuth). Save reference to Users's
        UserSocialAuth and import activities.
        '''
        if created:
            # save reference to our user's UserSocialAuth document
            u = document.user
            u.social_auth = document
            u.save()

            # queue up task to fetch activity data
            from .tasks import import_activities
            import_activities.delay(u.id)

signals.post_save.connect(UserSocialAuth.post_save, sender=UserSocialAuth)


class Storage(DjangoStorage):
    user = UserSocialAuth


class FitbitOAuth(BaseOAuth1):
    name = 'fitbit'

    AUTHORIZATION_URL = 'https://www.fitbit.com/oauth/authorize'
    REQUEST_TOKEN_URL = 'https://api.fitbit.com/oauth/request_token'
    ACCESS_TOKEN_URL  = 'https://api.fitbit.com/oauth/access_token'

    def get_user_id(self, details, response):
        return details['user_id']

    def get_user_details(self, response):
        detail_to_user_mapping = {
            'avatar':    'avatar',
            'birthdate': 'dateOfBirth',
            'city':      'city',
            'country':   'country',
            'full_name': 'fullName',
            'gender':    'gender',
            'height':    'height',
            'nickname':  'nickname',
            'state':     'state',
            'user_id':   'encodedId',
            'username':  'displayName',
            'weight':    'weight',
        }

        user_details = dict((k,response.get(v, '')) for k,v in detail_to_user_mapping.items())
        user_details['email'] = ''
        user_details['gender'] = user_details['gender'].lower()

        return user_details

    def user_data(self, access_token, *args, **kwargs):
        user_data = self.get_json('https://api.fitbit.com/1/user/-/profile.json', auth=self.oauth_auth(access_token))
        return user_data['user']

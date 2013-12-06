from celery import shared_task
from datetime import datetime, timedelta
from mongoengine import NotUniqueError

from .models import Activity, Competition, User
from .utils import date_range


@shared_task
def update_activity(user, date):
    '''
    Create or update user activity for a given date.
    '''
    # we only care about year/month/date
    date = datetime(year=date.year, month=date.month, day=date.day)

    # get or create activity
    activity, created = Activity.objects.get_or_create(user=user, date=date)

    # update with response from fitbit
    for k,v in user.get_activities(date).items():
        setattr(activity, k, v)

    # save activity, add to user's embedded list of activities if it's new
    activity.save()
    if created:
        user.activities.append(activity)
        user.save()

@shared_task()
def update_activities():
    '''
    Update activities for all users.
    '''
    now = datetime.utcnow()

    for user in User.objects.all():
        for date in date_range(now - timedelta(days=3), now):
            update_activity(user, date)


@shared_task()
def import_activities(uid):
    '''
    Import activities for user.
    '''
    user = User.objects.get(id=uid)
    competition = Competition.objects.get()
    now = datetime.utcnow()

    for date in date_range(competition.start, now):
        update_activity(user, date)

from celery import shared_task
from datetime import datetime
from mongoengine import NotUniqueError

from .models import Activity, Competition, User
from .utils import date_range


@shared_task()
def update_activities():
    '''
    Update activities for users.
    '''
    now = datetime.utcnow()
    date = datetime(year=now.year, month=now.month, day=now.day)
    for u in User.objects.all():
        a = Activity.objects(user=u, date=date).first()
        if a:
            for k,v in u.get_activities(date).items():
                setattr(a, k, v)
        else:
            a = Activity(user=u, date=date, **u.get_activities(date))
            u.activities.append(a)
        try:
            a.save()
            u.save()
        except NotUniqueError:
            pass


@shared_task()
def import_activities(uid):
    '''
    Import activities for user.
    '''
    u = User.objects.get(id=uid)
    c = Competition.objects.get()

    now = datetime.utcnow()

    for date in date_range(c.start, now):
        a = Activity(user=u, date=date, **u.get_activities(date))
        try:
            a.save()
            u.activities.append(a)
        except NotUniqueError:
            pass

    u.save()

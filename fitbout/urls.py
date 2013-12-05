from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'fitbout.app.views.home'),
    url(r'^about/$', 'fitbout.app.views.about'),
    url(r'^leaderboard/$', 'fitbout.app.views.leaderboard'),
    url(r'^profile/$', 'fitbout.app.views.profile'),
    url(r'^login/$', 'fitbout.app.views.login'),
    url(r'^logout/$', 'fitbout.app.views.logout'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
)

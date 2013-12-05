from django.contrib.auth import logout as _logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from .models import Competition


def login(request):
    if request.user.is_authenticated():
        return redirect('/')
    return render_to_response('login.jade', {}, RequestContext(request))


@login_required
def home(request):
    return render_to_response('home.jade', {'user': request.user}, RequestContext(request))


@login_required
def leaderboard(request):
    c = Competition.objects.get()
    ctx = {
        'user': request.user,
        'male_steps': c.stats['male_steps'],
        'female_steps': c.stats['female_steps'],
        'male_most_steps': c.stats['male_most_steps'],
        'female_most_steps': c.stats['female_most_steps'],
    }
    return render_to_response('leaderboard.jade', ctx, RequestContext(request))


@login_required
def about(request):
    return render_to_response('about.jade', {'user': request.user}, RequestContext(request))


@login_required
def profile(request):
    return render_to_response('profile.jade', {'user': request.user}, RequestContext(request))


@login_required
def logout(request):
    _logout(request)
    return redirect('/')


from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^', views.home, name='posts'),
    url(r'^(?P<username>\w+)/$', views.profile, name='profile'),
    url(r'^(?P<username>\w+)/followers/$', views.profile_followers, name='profile_followers'),
    url(r'^users/follow/$', views.user_follow, name='user_follow'),
]


from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^(?P<slug>[-\w]+)/$', views.post, name='post'),
    url(r'^', views.posts, name='posts'),
]

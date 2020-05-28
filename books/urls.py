
from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^(?P<slug>[-\w]+)/$', views.detail, name='book'),
    url(r'^$', views.list, name='books'),
]

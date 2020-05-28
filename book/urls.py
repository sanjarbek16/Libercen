from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView

from rest_framework import routers

import users.views as users_views
import books.views as books_views
import api.views as api_views
import posts.views as posts_views
import activities.views as activities_views
import basic.views as basic



favicon_view = RedirectView.as_view(url='/static/icons/favicon.ico', permanent=True)

router = routers.DefaultRouter()
router.register(r'books', api_views.BookViewSet)
router.register(r'reviews', api_views.ReviewViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^react/', TemplateView.as_view(template_name="index.html")),
    url(r'^api', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^blog/', include('blog.urls')),
    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    url(r'^settings/$', users_views.settings, name='settings'),
    url(r'^books/', include('books.urls')),
    url(r'^notifications/$', activities_views.notifications, name='notifications'),
    url(r'^(?P<username>[\w.@]+)/$', users_views.profile, name='profile'),
    url(r'^(?P<username>[\w.@]+)/followers/$', users_views.profile_followers, name='profile_followers'),
    url(r'^(?P<username>[\w.@]+)/following/$', users_views.profile_following, name='profile_following'),
    url(r'^(?P<username>[\w.@]+)/info/$', users_views.profile_info, name='profile_info'),
    url(r'^(?P<username>[\w.@]+)/favourite-books/$', users_views.profile_fav_books, name='profile_fav_books'),
    url(r'^$', users_views.home, name='home'),
    url(r'^privacy-policy/$', basic.policy, name='privacy-policy'),
    url(r'^users/follow/$', users_views.user_follow, name='user_follow'),
    url(r'^b/add-fav/$', books_views.add_fav, name='add_fav'),
    url(r'^p/like/$', posts_views.post_like, name='post_like'),
    url(r'^r/like/$', books_views.review_like, name='review_like'),
    url(r'^r/delete/$', books_views.review_delete, name='review_delete'),
    url(r'^r/comment/$', books_views.review_comment, name='review_comment'),
    url(r'^r/comment/delete/$', books_views.comment_delete, name='review_comment_delete'),
    url(r'^b/add/$', books_views.book_create, name='create'),
    url(r'^p/post/$', posts_views.post_write, name='write'),
    url(r'^p/comment/$', posts_views.post_comment, name='post_comment'),
    url(r'^p/comment/delete/$', posts_views.comment_delete, name='post_comment_delete'),
    url(r'^p/(?P<id>\d+)/$', posts_views.post_detail, name='post_detail'),
    url(r'^p/delete/$', posts_views.post_delete, name='post_delete'),
    url(r'^notifications/last/$', activities_views.last_notifications,
        name='last_notifications'),
    url(r'^user/menu/$', basic.user_menu,
        name='user_menu'),
    url(r'^notifications/check/$', activities_views.check_notifications,
        name='check_notifications'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

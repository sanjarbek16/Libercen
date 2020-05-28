from django.db import models
from django.conf import settings 
from django.contrib.auth.models import User
import urllib
import hashlib
import os.path
from django.db.models.signals import post_save
from django.utils.timezone import now as timezone_now
from activities.models import Notification


def upload_to(instance, filename):
    now = timezone_now()
    filename_base, filename_ext = os.path.splitext(filename)
    return "profile/%s%s" % (
        now.strftime("%Y/%m/%Y%m%d%H%M%S"),
        filename_ext.lower(),)


def upload_back(instance, filename):
    now = timezone_now()
    filename_base, filename_ext = os.path.splitext(filename)
    return "profile/back_image/%s%s" % (
        now.strftime("%Y/%m/%Y%m%d%H%M%S"),
        filename_ext.lower(),)


class Profile(models.Model):
    user = models.OneToOneField(User)
    about = models.TextField(max_length=200, blank=True, null=True)
    url = models.CharField(max_length=50, null=True, blank=True)
    avatar = models.ImageField(upload_to=upload_to, null=True, blank=True)
    back_image = models.ImageField(upload_to=upload_back, null=True, blank=True)
    fav_books = models.ManyToManyField('books.Book', through='books.Favourite')
    # reputation = models.IntegerField(default=0)
    # language = models.CharField(max_length=5, default='en')

    class Meta:
        db_table = 'auth_profile'

    def get_url(self):
        url = self.url
        if "http://" not in self.url and "https://" not in self.url and len(self.url) > 0:
            url = "http://" + str(self.url)

        return url

    def get_screen_name(self):
        try:
            if self.user.get_full_name():
                return self.user.get_full_name()
            else:
                return self.user.username
        except:
            return self.user.username

    def notify_liked(self, post):
        if self.user != post.user:
            Notification(notification_type=Notification.LIKED,
                         from_user=self.user, to_user=post.user,
                         post=post).save()

    def notify_followed(self, user):
        if self.user != user:
            Notification(notification_type=Notification.FOLLOWED,
                         from_user=self.user, to_user=user,
                         user=user).save()

    def unotify_followed(self, user):
        if self.user != user:
            Notification.objects.filter(notification_type=Notification.FOLLOWED,
                         from_user=self.user, to_user=user,
                         user=user).delete()
            
    def notify_commented(self, post):
        if self.user != post.user:
            Notification(notification_type=Notification.COMMENTED,
                         from_user=self.user, to_user=post.user,
                         post=post).save()

    def unotify_commented(self, post):
        if self.user != post.user:
            Notification.objects.filter(notification_type=Notification.COMMENTED,
                         from_user=self.user, to_user=post.user,
                         post=post).delete()             

    def notify_review_liked(self, review):
        if self.user != review.user:
            Notification(notification_type=Notification.REVIEW_LIKED,
                         from_user=self.user, to_user=review.user,
                         review=review).save()

    def unotify_review_liked(self, review):
        if self.user != review.user:
            Notification.objects.filter(notification_type=Notification.REVIEW_LIKED,
                         from_user=self.user, to_user=review.user,
                         review=review).delete()

    def notify_post_liked(self, post):
        if self.user != post.user:
            Notification(notification_type=Notification.POST_LIKED,
                         from_user=self.user, to_user=post.user,
                         post=post).save()

    def unotify_post_liked(self, post):
        if self.user != post.user:
            Notification.objects.filter(notification_type=Notification.POST_LIKED,
                         from_user=self.user, to_user=post.user,
                         post=post).delete()

    def notify_image_liked(self, image):
        if self.user != image.user:
            Notification(notification_type=Notification.IMAGE_LIKED,
                         from_user=self.user, to_user=image.user,
                         image=image).save()

    def unotify_image_liked(self, image):
        if self.user != image.user:
            Notification.objects.filter(notification_type=Notification.IMAGE_LIKED,
                                        from_user=self.user, to_user=image.user,
                                        image=image).delete()

    def notify_image_commented(self, image):
        if self.user != image.user:
            Notification(notification_type=Notification.IMAGE_COMMENTED,
                         from_user=self.user, to_user=image.user,
                         image=image).save()

    def unotify_liked(self, post):
        if self.user != post.user:
            Notification.objects.filter(notification_type=Notification.LIKED,
                                        from_user=self.user, to_user=post.user,
                                        post=post).delete()           

    def notify_also_commented(self, feed):
        comments = feed.get_comments()
        users = []
        for comment in comments:
            if comment.user != self.user and comment.user != feed.user:
                users.append(comment.user.pk)

        users = list(set(users))
        for user in users:
            Notification(notification_type=Notification.ALSO_COMMENTED,
                         from_user=self.user,
                         to_user=User(id=user), feed=feed).save()

    def notify_favorited(self, question):
        if self.user != question.user:
            Notification(notification_type=Notification.FAVORITED,
                         from_user=self.user, to_user=question.user,
                         question=question).save()

    def unotify_favorited(self, question):
        if self.user != question.user:
            Notification.objects.filter(
                notification_type=Notification.FAVORITED,
                from_user=self.user,
                to_user=question.user,
                question=question).delete()

    def notify_answered(self, question):
        if self.user != question.user:
            Notification(notification_type=Notification.ANSWERED,
                         from_user=self.user,
                         to_user=question.user,
                         question=question).save()

    def notify_accepted(self, answer):
        if self.user != answer.user:
            Notification(notification_type=Notification.ACCEPTED_ANSWER,
                         from_user=self.user,
                         to_user=answer.user,
                         answer=answer).save()

    def unotify_accepted(self, answer):
        if self.user != answer.user:
            Notification.objects.filter(
                notification_type=Notification.ACCEPTED_ANSWER,
                from_user=self.user,
                to_user=answer.user,
                answer=answer).delete()


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)


class Contact(models.Model):
    user_from = models.ForeignKey(User,related_name='rel_from_set')
    user_to = models.ForeignKey(User, related_name='rel_to_set')
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return '{} follows {}'.format(self.user_from, self.user_to)


# Add following field to User dynamically
User.add_to_class('following',
                  models.ManyToManyField('self',
                                         through=Contact,
                                         related_name='followers',
                                         symmetrical=False))
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.text import slugify
from datetime import datetime
from django.utils.timezone import now as timezone_now
import os
from django.utils import timezone
from ckeditor.fields import RichTextField
from users.models import Profile
from activities.models import Activity
import unidecode
from unidecode import unidecode
from taggit_autosuggest.managers import TaggableManager


def upload_to(instance, filename):
    now = timezone_now()
    filename_base, filename_ext = os.path.splitext(filename)
    return "books/%s%s" % (now.strftime("%Y/%m/%Y%m%d%H%M%S"), filename_ext.lower(),)


class Book(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, blank=True, null=True)
    first_published = models.DateField()
    publisher = models.CharField(max_length=200, blank=True, null=True)
    ISBN = models.CharField(max_length=50, blank=True, null=True)
    edition = models.CharField(max_length=100, blank=True, null=True)
    page_count = models.IntegerField(blank=True, null=True)
    author = models.CharField(max_length=200)
    user = models.ForeignKey(User, related_name="books_added")
    genre = TaggableManager(verbose_name="Genre", help_text="Select from suggestions as you type the name of the genre. If there is no genre you are looking for type comma after writing it.", through=None, blank=False)
    about = RichTextField()
    language = models.CharField(max_length=200)
    original_language = models.CharField(max_length=200, blank=True, null=True)
    cover = models.ImageField(upload_to=upload_to, null=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-create_date',)
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(unidecode(self.name))
        super(Book, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('book', args=[self.slug])


class Review(models.Model):
    book = models.ForeignKey(Book, related_name='reviews')
    user = models.ForeignKey(User, related_name='reviews')
    review = RichTextField()
    date = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return 'Review by {} on {}'.format(self.user, self.book)

    def calculate_likes(self):
        likes = Activity.objects.filter(activity_type=Activity.LIKE,
                                        review=self.pk).count()
        self.likes = likes
        self.save()
        return self.likes

    def get_likes(self):
        likes = Activity.objects.filter(activity_type=Activity.LIKE,
                                        review=self.pk)
        return likes

    def get_likers(self):
        likes = self.get_likes()
        likers = []
        for like in likes:
            likers.append(like.user)
        return likers


class Comment(models.Model):
    review = models.ForeignKey(Review, related_name='comments')
    user = models.ForeignKey(User, related_name='comments_on_reviews')
    comment = models.TextField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ('-date',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.user, self.review)

    def calculate_likes(self):
        likes = Activity.objects.filter(activity_type=Activity.LIKE,
                                        review=self.pk).count()
        self.likes = likes
        self.save()
        return self.likes

    def get_likes(self):
        likes = Activity.objects.filter(activity_type=Activity.LIKE,
                                        review=self.pk)
        return likes

    def get_likers(self):
        likes = self.get_likes()
        likers = []
        for like in likes:
            likers.append(like.user)
        return likers


class Favourite(models.Model):
    profile = models.ForeignKey(Profile, related_name='fav_from_set', null=True)
    book = models.ForeignKey(Book, related_name='fav_to_set')
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return '{} likes {}'.format(self.profile, self.book)


# Add following field to User dynamically

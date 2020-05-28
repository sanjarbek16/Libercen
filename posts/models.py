from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from activities.models import Activity
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField


class Post(models.Model):
    user = models.ForeignKey(User, related_name='posts')
    post = RichTextUploadingField('contents')
    date = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ('-date',)

    def __str__(self):
        return 'Post by {}'.format(self.user)

    def get_absolute_url(self):
        return reverse('post_detail', args=[self.id])

    def calculate_likes(self):
        likes = Activity.objects.filter(activity_type=Activity.LIKE,
                                        post=self.pk).count()
        self.likes = likes
        self.save()
        return self.likes

    def get_likes(self):
        likes = Activity.objects.filter(activity_type=Activity.LIKE,
                                        post=self.pk)
        return likes

    def get_likers(self):
        likes = self.get_likes()
        likers = []
        for like in likes:
            likers.append(like.user)
        return likers


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments')
    user = models.ForeignKey(User, related_name='comments')
    comment = models.TextField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ('-date',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.user, self.post)




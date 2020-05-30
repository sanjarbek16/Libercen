from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.html import escape
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe


class Action(models.Model):
    user = models.ForeignKey(User,
                             related_name='actions',
                             db_index=True)
    verb = models.CharField(max_length=255)
    parent = models.ForeignKey('Action', null=True, blank=True)
    target_ct = models.ForeignKey(ContentType,
                                  blank=True,
                                  null=True,
                                  related_name='target_obj')
    target_id = models.PositiveIntegerField(null=True,
                                            blank=True,
                                            db_index=True)
    target = GenericForeignKey('target_ct', 'target_id')
    date = models.DateTimeField(auto_now_add=True,
                                db_index=True)

    class Meta:
        ordering = ('-date',)

    @staticmethod
    def get_feeds(from_feed=None):
        if from_feed is not None:
            feeds = Action.objects.filter(parent=None, id__lte=from_feed)
        else:
            feeds = Action.objects.filter(parent=None)
        return feeds

    @staticmethod
    def get_feeds_after(feed):
        feeds = Action.objects.filter(parent=None, id__gt=feed)
        return feeds


class Activity(models.Model):
    FAVORITE = 'F'
    LIKE = 'L'
    UP_VOTE = 'U'
    DOWN_VOTE = 'D'
    ACTIVITY_TYPES = (
        (FAVORITE, 'Favorite'),
        (LIKE, 'Like'),
        (UP_VOTE, 'Up Vote'),
        (DOWN_VOTE, 'Down Vote'),
    )

    user = models.ForeignKey(User)
    activity_type = models.CharField(max_length=1, choices=ACTIVITY_TYPES)
    date = models.DateTimeField(auto_now_add=True)
    post = models.IntegerField(null=True, blank=True)
    review = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'

    def __str__(self):
        return self.activity_type


# def save(self, *args, **kwargs):
#        super(Activity, self).save(*args, **kwargs)
#        if self.activity_type == Activity.FAVORITE:
#            Question = models.get_model('questions', 'Question')
#            question = Question.objects.get(pk=self.question)
#            user = question.user
#            user.profile.reputation = user.profile.reputation + 5
#            user.save()


class Notification(models.Model):
    LIKED = 'L'
    COMMENTED = 'C'
    FOLLOWED = 'F'
    IMAGE_LIKED = 'I'
    IMAGE_COMMENTED = 'N'
    ANSWERED = 'A'
    ACCEPTED_ANSWER = 'W'
    EDITED_ARTICLE = 'E'
    ALSO_COMMENTED = 'S'
    REVIEW_LIKED = 'R'
    POST_LIKED = 'P'
    NOTIFICATION_TYPES = (
        (LIKED, 'Liked'),
        (COMMENTED, 'Commented'),
        (FOLLOWED, 'Followed'),
        (ANSWERED, 'Answered'),
        (ACCEPTED_ANSWER, 'Accepted Answer'),
        (EDITED_ARTICLE, 'Edited Article'),
        (ALSO_COMMENTED, 'Also Commented'),
        (IMAGE_LIKED, 'Image Liked'),
        (IMAGE_COMMENTED, 'Image Commented'),
        (REVIEW_LIKED, 'Review Liked'),
        (POST_LIKED, 'Post Liked')
    )

    _LIKED_TEMPLATE = u'<a href="/{0}/"><strong>{0}</strong></a> liked your post'
    _IMAGE_LIKED_TEMPLATE = u'<a href="/{0}/"><strong>{0}</strong></a> liked your image <img src="https://libercen.s3.amazonaws.com/{1}/" style="float:right;" class="user-picture">'
    _POST_LIKED_TEMPLATE = u'<a href="/{0}/"><strong>{0}</strong></a> liked your post <strong>{1}</p></strong>'
    _REVIEW_LIKED_TEMPLATE = u'<a href="/{0}/"><strong>{0}</strong></a> liked your review on book <strong>{1}</strong>'
    _COMMENTED_IMAGE_TEMPLATE = u'<a href="/{0}/"><strong>{0}</strong></a> commented on your image'
    _FOLLOW_TEMPLATE = u'<a href="/{0}/"><strong>{0}</strong></a> is now following you'
    _COMMENTED_TEMPLATE = u'<a href="/{0}/"><strong>{0}</strong></a> commented on your post <strong>{1}</p></strong>'
    _ANSWERED_TEMPLATE = u'<a href="/{0}/"><strong>{0}</strong></a> answered your question: <a href="/questions/{2}/">{3}</a>'
    _ACCEPTED_ANSWER_TEMPLATE = u'<a href="/{0}/"><strong>{0}</strong></a> accepted your answer: <a href="/questions/{2}/">{3}</a>'
    _EDITED_ARTICLE_TEMPLATE = u'<a href="/{0}/"><strong>{0}</strong></a> edited your article: <a href="/article/{2}/">{3}</a>'
    _ALSO_COMMENTED_TEMPLATE = u'<a href="/{0}/"><strong>{0}</strong></a> also commentend on the post: <a href="/feeds/{2}/">{3}</a>'

    from_user = models.ForeignKey(User, related_name='+')
    to_user = models.ForeignKey(User, related_name='+')
    date = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=1, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey(User, null=True, blank=True)
    review = models.ForeignKey('books.Review', null=True, blank=True)
    post = models.ForeignKey('posts.Post', null=True, blank=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ('-date',)

    def __str__(self):
        if self.notification_type == self.LIKED:
            return self._LIKED_TEMPLATE.format(
                escape(self.from_user.username),
            )
        elif self.notification_type == self.COMMENTED:
            return self._COMMENTED_TEMPLATE.format(
                escape(self.from_user.username),
                escape(self.get_summary(self.post.post)),
            )
        elif self.notification_type == self.ANSWERED:
            return self._ANSWERED_TEMPLATE.format(
                escape(self.from_user.username),
                escape(self.from_user.profile.get_screen_name()),
                self.question.pk,
                escape(self.get_summary(self.question.title))
            )
        elif self.notification_type == self.ACCEPTED_ANSWER:
            return self._ACCEPTED_ANSWER_TEMPLATE.format(
                escape(self.from_user.username),
                escape(self.from_user.profile.get_screen_name()),
                self.answer.question.pk,
                escape(self.get_summary(self.answer.description))
            )
        elif self.notification_type == self.EDITED_ARTICLE:
            return self._EDITED_ARTICLE_TEMPLATE.format(
                escape(self.from_user.username),
                escape(self.from_user.profile.get_screen_name()),
                self.article.slug,
                escape(self.get_summary(self.article.title))
            )
        elif self.notification_type == self.ALSO_COMMENTED:
            return self._ALSO_COMMENTED_TEMPLATE.format(
                escape(self.from_user.username),
                escape(self.from_user.profile.get_screen_name()),
                self.feed.pk,
                escape(self.get_summary(self.feed.post))
            )
        elif self.notification_type == self.IMAGE_COMMENTED:
            return self._IMAGE_COMMENTED_TEMPLATE.format(
                escape(self.from_user.username),
                escape(self.image.image),
            )
        elif self.notification_type == self.FOLLOWED:
            return self._FOLLOW_TEMPLATE.format(
                escape(self.from_user.username),
            )
        elif self.notification_type == self.REVIEW_LIKED:
            return self._REVIEW_LIKED_TEMPLATE.format(
                escape(self.from_user.username),
                escape(self.review.book.name),
            )
        elif self.notification_type == self.POST_LIKED:
            return self._POST_LIKED_TEMPLATE.format(
                escape(self.from_user.username),
                escape(self.get_summary(self.post.post)),
            )
        else:
            return 'Something went wrong.'

    def get_summary(self, value):
        summary_size = 70
        value = mark_safe(value)
        value = strip_tags(value)
        if len(value) > summary_size:
            return u'{0}...'.format(value[:summary_size])

        else:
            return value
